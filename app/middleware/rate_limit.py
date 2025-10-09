# app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Create limiter instance — identify users by IP
limiter = Limiter(key_func=get_remote_address)


# Exception handler for rate limit exceeded
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error": str(exc),
        },
    )


# Function to register limiter with FastAPI app
def setup_rate_limiter(app):
    """
    Integrate the rate limiter into the FastAPI application.
    Should be called in main.py after app initialization.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter
