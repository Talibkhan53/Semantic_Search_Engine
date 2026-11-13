from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
     """Application settings, read from environment variables or a .env file."""

     model_config = SettingsConfigDict(env_file=".env" , extra="ignore") #Ignore Here Removes Extra Variables if present in .env file insteal of giveing error

     chroma_path : str = "./chroma_data"
     collection_name : str = "documents"
     embedding_model : str = "all-MiniLM-L6-v2"

     chunk_size : int = 150
     chunk_overlap : int = 30

     api_key: str = ""

     max_text_chars: int = 2_000_000

@lru_cache
def get_settings() -> Settings:
    return Settings()

