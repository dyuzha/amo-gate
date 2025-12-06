import json
import logging
from pathlib import Path
import pytest
from gate.amo.amo_client import AmoClient

logger = logging.getLogger(__name__)

def load_json(name: str):
    path = Path(__file__).parent / "data" / name
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_amo_client(amo_client: AmoClient):
    raw_data = load_json("booked.json")
    for j in raw_data:
        amo_client.update_booked_info(j)
