import json
import logging
from pathlib import Path
import pytest
from gate.amo.amo_client import AmoClient


logger = logging.getLogger(__name__)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



@pytest.mark.parametrize("pl_name", [ 'mc', 'booked'])
@pytest.mark.asyncio
async def test_amo_client(
        amo_client: AmoClient,
        test_data_path: Path,
        pl_name: str
        ):
    path = test_data_path / f"{pl_name}.json"
    raw_data = load_json(path)
    for j in raw_data:
        amo_client.load_pipeline_lead_data(j, pl_name)
