from transformers import BertTokenizer, BertModel
import torch
from scipy.spatial.distance import cosine
class BertAnalyse:
    def __init__(self):
        #штука для превращения слов в токены
        self.tokenizer = BertTokenizer.from_pretrained('sberbank-ai/ruBert-base')
        self.model = BertModel.from_pretrained('sberbank-ai/ruBert-base')
    def get_mean_similarity(self, text1, text2, device='cpu'):
        tokenized_text1 = self.tokenizer.tokenize(text1)
        tokenized_text2 = self.tokenizer.tokenize(text2)
        # Разделяем токенизированный текст на части по 512 токенов
        max_chunk_size = 512 - 2  # уменьшаем на 2, чтобы вместить специальные токены [CLS] и [SEP]
        chunks_text1 = [tokenized_text1[i:i + max_chunk_size] for i in range(0, len(tokenized_text1), max_chunk_size)]
        chunks_text2 = [tokenized_text2[i:i + max_chunk_size] for i in range(0, len(tokenized_text2), max_chunk_size)]
        # Инициализируем пустой список для эмбеддингов
        chunk_compare = []
        for chunk1,chunk2 in zip(chunks_text1,chunks_text2):
            # Добавляем специальные токены в начало и конец части
            chunk1 = ['[CLS]'] + chunk1 + ['[SEP]']
            chunk2 = ['[CLS]'] + chunk2 + ['[SEP]']
            # Конвертируем список токенов в тензоры
            inputs1 = self.tokenizer.encode_plus(chunk1, return_tensors='pt', padding=True, truncation=True, max_length=512)
            inputs1 = inputs1.to(device)
            inputs2 = self.tokenizer.encode_plus(chunk2, return_tensors='pt', padding=True, truncation=True, max_length=512)
            inputs2 = inputs2.to(device)
            # Получаем выходные данные модели
            with torch.no_grad():
                outputs1 = self.model(**inputs1)
                outputs2 = self.model(**inputs2)
            # Берем эмбеддинги от последнего слоя модели BERT
            last_hidden_states1 = outputs1.last_hidden_state
            last_hidden_states2 = outputs2.last_hidden_state
            # Берем эмбеддинг для [CLS] токена
            chunk_embedding1 = torch.mean(last_hidden_states1, dim=1).squeeze()
            chunk_embedding2 = torch.mean(last_hidden_states2, dim=1).squeeze()
            chunk_compare.append(1 - cosine(chunk_embedding1, chunk_embedding2))
        if chunk_compare:
            mean_similarity = sum(chunk_compare) / len(chunk_compare)
        else:
            mean_similarity = 0
        return mean_similarity
    def compare_text(self,text1, text2):
        return self.get_mean_similarity(text1,text2)