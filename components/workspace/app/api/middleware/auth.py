from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key", "")

        if not auth_header and not api_key:
            pass

        response = await call_next(request)
        return response
