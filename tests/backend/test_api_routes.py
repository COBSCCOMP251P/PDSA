import pytest
import httpx
from shared.backend.main import app


@pytest.mark.asyncio
async def test_init_game_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "player_name": "Tester",
            "board_size": 6,
            "email": None
        }
        resp = await client.post("/api/snake-ladder/init", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert "session_id" in data
        assert "board_config" in data
        assert "answer_choices" in data
        assert data["board_config"]["board_size"] == 6


@pytest.mark.asyncio
async def test_submit_answer_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        init_payload = {
            "player_name": "Tester",
            "board_size": 6,
            "email": None
        }
        init_resp = await client.post("/api/snake-ladder/init", json=init_payload)
        assert init_resp.status_code == 201
        init_data = init_resp.json()
        session_id = init_data["session_id"]

        submit_payload = {
            "session_id": session_id,
            "player_answer": 0
        }
        submit_resp = await client.post("/api/snake-ladder/submit", json=submit_payload)
        assert submit_resp.status_code == 200
        data = submit_resp.json()
        assert "is_correct" in data
        assert "correct_answer" in data
        assert "bfs_result" in data
        assert "dfs_result" in data
