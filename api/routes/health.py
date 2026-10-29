from fastapi import APIRouter
from api.routes.dependencies import engine
router = APIRouter()

@router.get("/health")
def health_check():
    """Check Whether API Is Running"""
    return {"Status":"Healthy"}