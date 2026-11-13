import logging

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(request: Request):
    """Report readiness. Returns 503 if the model or Chroma is unavailable."""
    engine = getattr(request.app.state, "engine", None)

    if engine is None:
        raise HTTPException(status_code=503, detail="Search engine is not ready")

    try:
        return {"status": "ok", "chroma": "ok", **engine.stats()}
    except Exception as exc:
        logger.exception("Health check failed")
        raise HTTPException(status_code=503, detail="Vector store unavailable") from exc