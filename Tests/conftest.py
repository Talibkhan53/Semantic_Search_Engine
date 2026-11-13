import hashlib
import math

import pytest
from fastapi.testclient import TestClient

from app.Chunking.chunking import Chunker
from app.config import Settings, get_settings
from app.main import app
from app.Services.search_engine import SearchEngine
from app.VectorStore.vector_store import VectorStore


class FakeEmbedder:
    """Deterministic bag-of-words hashing embedder. No model download needed."""

    model_name = "fake-hash-embedder"
    DIM = 128

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.DIM
        for word in text.lower().split():
            word = word.strip(".,!?;:\"'()")
            if not word:
                continue
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.DIM
            v[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, query):
        return self._vec(query)


def make_client(tmp_path, api_key: str = "", chunk_size: int = 150, overlap: int = 30):
    engine = SearchEngine(
        chunker=Chunker(chunk_size, overlap),
        embedder=FakeEmbedder(),  # type: ignore[arg-type]
        store=VectorStore(str(tmp_path / "chroma"), "test_documents"),
    )
    app.state.engine = engine
    app.dependency_overrides[get_settings] = lambda: Settings(api_key=api_key)
    return TestClient(app)


@pytest.fixture
def client(tmp_path):
    yield make_client(tmp_path)
    app.dependency_overrides.clear()
    app.state.engine = None


@pytest.fixture
def auth_client(tmp_path):
    yield make_client(tmp_path, api_key="secret")
    app.dependency_overrides.clear()
    app.state.engine = None