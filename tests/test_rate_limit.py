import json
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.middleware.rate_limit import _rate_limit_exceeded_handler


# ✅ Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@pytest.fixture
def client():
    """Create a FastAPI app with rate limiting enabled for testing."""
    app = FastAPI()

    @app.get("/limited")
    @limiter.limit("15/minute")
    async def limited_route(request: Request):
        return {"message": "OK"}

    setup_rate_limiter(app)
    return TestClient(app)


# ✅ Test 1 — under limit
def test_rate_limit_under_limit(client):
    for _ in range(10):
        response = client.get("/limited")
        assert response.status_code == 200
        assert response.json()["message"] == "OK"


# ✅ Test 2 — exceed limit
def test_rate_limit_exceeded(client):
    for _ in range(15):
        client.get("/limited")

    response = client.get("/limited")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text


# ✅ Test 3 — handler direct call (final fixed)
@pytest.mark.asyncio
async def test_rate_limit_handler_direct_call():
    request = Request(scope={"type": "http"})

    class DummyLimit:
        def __init__(self, limit: str):
            self.limit = limit
            self.error_message = f"Rate limit of {limit} exceeded"

    dummy_limit = DummyLimit("15/minute")
    exc = RateLimitExceeded(dummy_limit)

    response = await _rate_limit_exceeded_handler(request, exc)

    assert response.status_code == 429

    # ✅ Properly decode JSONResponse body
    json_resp = json.loads(response.body.decode("utf-8"))
    assert "Rate limit exceeded" in json_resp["detail"]
