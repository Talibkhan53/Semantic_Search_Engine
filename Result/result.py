
from dataclasses import dataclass


@dataclass
class SearchResult:
    file_name: str
    score: float
    text: str
    chunk_index: int
    distance: float

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_name,
            "score": self.score,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "distance": self.distance,
        }
