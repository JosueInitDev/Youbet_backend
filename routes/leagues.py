from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/leagues", tags=["Leagues"])

BASE = Path("leagues")  # folder where leagues.json is stored


@router.get("")
def get_leagues():
    """
    Return all saved leagues from leagues/leagues.json
    """
    file = BASE / "leagues.json"

    if not file.exists():
        raise HTTPException(status_code=404, detail="Leagues file not found")

    try:
        return json.loads(file.read_text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading leagues: {e}")
