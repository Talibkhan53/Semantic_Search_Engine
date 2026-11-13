
class Chunker:
    """Split text into overlapping chunks using a word-level sliding window."""
    def __init__(self,chunk_size: int = 150,chunk_overlap: int = 30) -> None :

        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> list[str]:
       if not text or not text.strip():
            return []

       words = text.split()

       step = self.chunk_size - self.chunk_overlap
       chunks: list[str] = []

       for start in range(0,len(words),step):
           chunks.append(" ".join(words[start:start + self.chunk_size]))

           if start + self.chunk_size >= len(words):
                break

       return chunks    
