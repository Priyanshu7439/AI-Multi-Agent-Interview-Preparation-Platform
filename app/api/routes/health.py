from fastapi import APIRouter
from typing import Dict

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """Check the health status of the application API and connectivity."""
    return {"status": "healthy", "service": "AI Interview Prep Platform"}
