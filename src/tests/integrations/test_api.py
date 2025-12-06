from pathlib import Path
import json
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_webhook_booked():
    payload_path = Path(__file__).parent.parent / "data" / "booked.json"

    with payload_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    async with AsyncClient(
        base_url="https://localhost:9000",
        verify=False,
    ) as client:
        response = await client.post("/booked", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
