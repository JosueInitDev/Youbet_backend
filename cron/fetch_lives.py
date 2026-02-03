import os
import json
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://56.228.41.8/lives"
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN missing in .env")

FIXTURES_DIR = Path("fixtures")
LIVES_DIR = Path("lives")

LIVES_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 30  # seconds between calls


def has_live_match(fixtures: dict) -> bool:
    for match in fixtures.get("matches", []):
        status = match.get("event_status", "").lower()
        if status in ("Live"):
            return True
    return False


def load_fixtures(league_key: str):
    file = FIXTURES_DIR / f"{league_key}.json"
    if not file.exists():
        return None
    return json.loads(file.read_text())


def fetch_lives():
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
        fixtures = load_fixtures(league)

        if not fixtures:
            continue

        if not has_live_match(fixtures):
            print(f"[SKIP] {league} – no live match")
            continue

        print(f"[FETCH] live matches for {league}")

        try:
            r = httpx.get(
                API_URL,
                params={"league_key": league},
                headers=headers,
                timeout=20,
            )

            r.raise_for_status()

            LIVES_DIR.joinpath(f"{league}.json").write_text(
                json.dumps(r.json(), indent=2)
            )

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"[ERROR] {league}: {e}")


if __name__ == "__main__":
    fetch_lives()
