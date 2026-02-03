from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/lives", tags=["Lives"])

BASE = Path("lives")


@router.get("/{league_key}")
def get_lives(league_key: str):

    file = BASE / f"{league_key}.json"

    if not file.exists():
        raise HTTPException(404)

    return json.loads(file.read_text())
