from sentence_transformers import SentenceTransformer
import numpy as np

class Embedding:
    def __init__(self,model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_file(self,file_content):
        result = {}
        for file_name , file_data in file_content.items():
            embed_data = self.model.encode(file_data)
            result[file_name] = embed_data.tolist()
        return result



    def embed_query(self,query):
        return self.model.encode(query)