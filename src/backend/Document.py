import os
import uuid
import hashlib

class Document():
    def __init__(self,filepath: str):
        self.filepath = filepath
        self.type = filepath.split(".")[-1]
        self.uuid = uuid.uuid4()
        self.md5 = None
        self.basename = os.path.basename(filepath)
        
    def calculate_md5_hash(self):
        hasher =hashlib.md5()
        with open(self.filepath,"rb") as file:
            hasher.update(file.read())
        self.md5 = hasher.hexdigest()
            
        
        