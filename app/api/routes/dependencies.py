from fastapi import HTTPException, Request, status

from app.Services.search_engine import SearchEngine


def get_engine(request: Request) -> SearchEngine:
    engine = getattr(request.app.state, "engine", None)

    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search engine is not ready",
        )

    return engine