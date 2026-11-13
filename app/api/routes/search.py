import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.dependencies import get_engine
from app.schema import SearchRequest, SearchResponse
from app.security import require_api_key
from app.Services.search_engine import SearchEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"], dependencies=[Depends(require_api_key)])


@router.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    engine: SearchEngine = Depends(get_engine),
):
    try:
        return engine.search(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail="Search failed") from exc