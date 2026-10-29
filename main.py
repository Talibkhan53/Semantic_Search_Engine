from fastapi import FastAPI
from api.routes.health import router as health_router
from api.routes.documents import router as documents_router
from api.routes.search import router as search_router

app = FastAPI(
    title="Semantic Search Engine",
    description="API for document indexing and semantic search",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(search_router)
