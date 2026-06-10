from app.api.routes.resume import router as resume_router
from app.api.routes.job import router as job_router
from app.api.routes.interview import router as interview_router
from app.api.routes.health import router as health_router

__all__ = [
    "resume_router",
    "job_router",
    "interview_router",
    "health_router"
]
