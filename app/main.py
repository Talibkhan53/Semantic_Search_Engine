import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.Chunking.chunking import Chunker
from app.config import get_settings
from app.Embeddings.embedding import Embedder
from app.Services.search_engine import SearchEngine
from app.VectorStore.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Loading embedding model %s", settings.embedding_model)

    app.state.engine = SearchEngine(
        chunker=Chunker(settings.chunk_size, settings.chunk_overlap),
        embedder=Embedder(settings.embedding_model),
        store=VectorStore(settings.chroma_path, settings.collection_name),
    )
    logger.info("Search engine ready")

    yield

    app.state.engine = None


app = FastAPI(
    title="Semantic Search Engine",
    description="Document indexing and semantic search API",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(search_router)