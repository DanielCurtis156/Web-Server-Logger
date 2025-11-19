import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_ingest_empty_batch(monkeypatch):
    # fake insert_batch so we don't hit DB
    monkeypatch.setattr("main.insert_batch", lambda records: None)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/ingest", headers={"X-API-KEY": "secret123"}, json=[])
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "ingested": 0}

@pytest.mark.asyncio
async def test_ingest_rejects_large_batch(monkeypatch):
    monkeypatch.setattr("main.insert_batch", lambda records: None)
    events = [{"ts": "2025-11-18T03:30:00Z"}] * 2001
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/ingest", headers={"X-API-KEY": "secret123"}, json=events)
    assert resp.status_code == 413

@pytest.mark.asyncio
async def test_ingest_requires_api_key(monkeypatch):
    monkeypatch.setattr("main.insert_batch", lambda records: None)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/ingest", json=[])
    assert resp.status_code == 401