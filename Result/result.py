from dataclasses import dataclass

@dataclass
class SearchResult:
    file_name:str
    score:float
