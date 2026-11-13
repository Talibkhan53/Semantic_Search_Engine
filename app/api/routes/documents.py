import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.dependencies import get_engine
from app.config import Settings, get_settings
from app.schema import DeleteOut, DocumentIn, DocumentInfo, DocumentOut
from app.security import require_api_key
from app.Services.search_engine import SearchEngine

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(require_api_key)],
)


@router.post("", response_model=DocumentOut)
def index_document(
    doc: DocumentIn,
    engine: SearchEngine = Depends(get_engine),
    settings: Settings = Depends(get_settings),
):
    """Index (or re-index) a document. Re-sending identical text is a no-op."""
    if len(doc.text) > settings.max_text_chars:
        raise HTTPException(status_code=413, detail="Document text is too large")

    try:
        return engine.index_document(doc)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Indexing failed for %s", doc.document_id)
        raise HTTPException(status_code=500, detail="Indexing failed") from exc


@router.get("/{document_id}", response_model=DocumentInfo)
def get_document(document_id: str, engine: SearchEngine = Depends(get_engine)):
    info = engine.get_document(document_id)

    if info is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return info


@router.delete("/{document_id}", response_model=DeleteOut)
def delete_document(document_id: str, engine: SearchEngine = Depends(get_engine)):
    result = engine.delete_document(document_id)

    if result.deleted_chunks == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return result