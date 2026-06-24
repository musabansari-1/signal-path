from collections import defaultdict, deque
from time import monotonic

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings

AI_HEAVY_PATHS = (
    "/api/candidate-profile/analyze",
    "/api/resumes/generate",
    "/api/messages/generate",
    "/api/interview-prep/generate",
    "/api/weekly-plan/generate",
)


class AIRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method != "OPTIONS" and request.url.path in AI_HEAVY_PATHS:
            identity = request.client.host if request.client else "unknown"
            key = f"{identity}:{request.url.path}"
            now = monotonic()
            bucket = self.requests[key]
            while bucket and now - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= settings.ai_rate_limit_per_minute:
                return Response(
                    content="AI request rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="text/plain",
                )
            bucket.append(now)
        return await call_next(request)

