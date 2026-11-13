from typing import Literal
from pydantic import BaseModel, Field, field_validator

_ID_PATTERN = r"^[A-Za-z0-9_.\-]{1,128}$"

class DocumentIn(BaseModel):
    document_id : str = Field(pattern=_ID_PATTERN)
    file_name : str = Field(min_length=1 , max_length=256)
    text:str 
    user_id : str | None = Field(default=None,max_length=128)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls,value):
        if not  value.strip():
            raise ValueError("TEXT MUSNOT BE EMPTY")
        return value

class DocumentOut(BaseModel):
    document_id : str 
    file_name : str
    chunks : int
    status: Literal["indexed", "updated", "unchanged"]


class DocumentInfo(BaseModel):
    document_id: str
    file_name: str | None
    chunks: int
    user_id: str | None = None


class DeleteOut(BaseModel):
    document_id: str
    deleted_chunks: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=20)
    document_ids: list[str] | None = Field(default=None, max_length=100)
    user_id: str | None = None
    min_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    group_by_document: bool = False

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("query must contain at least 3 characters")
        return value


class SearchHit(BaseModel):
    document_id: str
    file_name: str
    chunk_index: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[SearchHit]