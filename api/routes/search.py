
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field,field_validator

from api.routes.dependencies import engine

logger = logging.getLogger(__name__)

router = APIRouter()


class SearchRequest(BaseModel):
    path: str = Field(min_length=1)
    query: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=20)


    @field_validator("query")
    @classmethod
    def validate_query(cls,value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Query must contain at least 3 characters")
        return value


@router.post("/search")
def search_documents(request: SearchRequest):
    document_path = Path(request.path).expanduser().resolve()

    if not document_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Directory does not exist",
        )

    if not document_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Path must be a directory",
        )

    try:
        results = engine.search(
            path=str(document_path),
            query=request.query.strip(),
            top_k=request.top_k,
        )

        return {
            "query": request.query.strip(),
            "count": len(results),
            "results": results,
        }

    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Search operation failed")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during search",
        ) from exc
