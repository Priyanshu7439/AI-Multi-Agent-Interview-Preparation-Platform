from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings, logger
from app.core.exceptions import PlatformException
from app.api.routes import resume_router, job_router, interview_router, health_router
from app.api.middleware import StructuredLoggingMiddleware

app = FastAPI(
    title="AI Multi-Agent Interview Preparation Platform",
    description="Production-grade multi-agent AI framework to help candidates prepare for job interviews.",
    version="1.0.0"
)

# 1. Global Exception Handler
@app.exception_handler(PlatformException)
async def platform_exception_handler(request: Request, exc: PlatformException) -> JSONResponse:
    logger.error(
        "Platform Exception Handled", 
        path=request.url.path, 
        status_code=exc.status_code, 
        message=exc.message
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled System Exception", 
        path=request.url.path, 
        error=str(exc)
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# 2. Add Logging Middleware
app.add_middleware(StructuredLoggingMiddleware)

# 3. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include Routers
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(interview_router)
app.include_router(health_router)

# 5. Root endpoint
@app.get("/")
def read_root():
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "docs_url": "/docs"
    }
