from src.backend.Document import Document
from src.backend.FileUtils import FileUtils
class DB():
    def __init__(self,paths):
        self._list = []
        self.paths = paths
        self.createDocuments()
        self._removed = []
    def createDocuments(self):
        for path in self.paths:
            self.append(Document(path))
            
    def calculateMD5Hash(self):
        for doc in self._list:
            doc.calculate_md5_hash()
    def removeByIndex(self,idx):
        FileUtils.deleteFile(self._list[idx].filepath)
        self._removed.append(self._list.pop(idx))
    def append (self,item):
         self._list.append(item)
    def __len__(self):
        return len(self._list)
    def __iter__(self):
        return iter(self._list)
    def __getitem__(self,idx):
        return self._list[idx]
        
    def removeCurrCopyMD5(self,curr):
        curr_md5=self._list[curr].md5   
        i=0
        while i < len(self):
            if i != curr and self._list[i].md5 == curr_md5:
                self.removeByIndex(i)
            else:
                i += 1
    def getRemoved(self):
        return self._removed
                