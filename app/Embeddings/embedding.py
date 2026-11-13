from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    """Wraps a Sentence Transformers model. Create once and reuse."""
    def __init__(self,model_name="all-MiniLM-L6-v2") ->None :
        self.model_name = "all-MiniLM-L6-v2"
        self.model  = SentenceTransformer(model_name)

    def embed_documents(self,text:list[str]) -> list[list[float]] :
        vectors : np.ndarray = self.model.encode(
            text,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        
        return vectors.tolist()


    def embed_query(self,query):
        return self.model.encode(query)