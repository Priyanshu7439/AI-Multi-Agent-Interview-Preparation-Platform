import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Log request receipt
        logger.info(
            "Incoming HTTP request",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            
            # Log exceptions/errors
            logger.error(
                "HTTP request processing error",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise e
