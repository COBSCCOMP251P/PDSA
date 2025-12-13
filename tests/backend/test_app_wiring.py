import pytest
import httpx
from shared.backend.main import app


@pytest.mark.asyncio
async def test_app_starts_and_routes_present():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Use a GET endpoint to avoid method-not-allowed
        resp = await client.get("/api/snake-ladder/leaderboard?limit=1")
        assert resp.status_code == 200
