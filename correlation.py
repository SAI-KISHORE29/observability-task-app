import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Context variable to hold correlation ID across the async task
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        corr_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_var.set(corr_id)
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = corr_id
        return response