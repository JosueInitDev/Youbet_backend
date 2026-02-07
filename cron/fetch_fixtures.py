import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

API_URL = "https://api-thefootballapi.vetcho.org/fixtures"
SAVE_DIR = Path("fixtures")

SAVE_DIR.mkdir(exist_ok=True)

if not API_TOKEN:
    raise RuntimeError("API_TOKEN missing from .env")

def run():
    leagues = [
        "premier_league",
        "ligue_1",
        "bundesliga",
        "serie_a",
        "eredivisie",
        "la_liga",
        "euro",
        "champions_league",
        "europa_league",
        "conference_league",
        "world_cup",
    ]

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    for league in leagues:
        try:
            r = httpx.get(
                f"{API_URL}/{league}?odds=true&limit=20",
                headers=headers,
                timeout=30,
            )
            r.raise_for_status()
            
            SAVE_DIR.joinpath(f"{league}.json").write_text(
                json.dumps(r.json(), indent=2)
            )
        except httpx.HTTPStatusError as e:
            # API returned HTTP error (404, 500, etc)
            print(f"[SKIP] {league} HTTP error: {e}")
        except httpx.RequestError as e:
            # Network / timeout errors
            print(f"[SKIP] {league} request failed: {e}")
        except Exception as e:
            # Any other error
            print(f"[SKIP] {league} unknown error: {e}")
        
    print("[FIXTURES] Done fetching all leagues")


if __name__ == "__main__":
    run()
