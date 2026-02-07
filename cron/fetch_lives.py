import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api-thefootballapi.vetcho.org/lives"
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN missing in .env")

LIVES_DIR = Path("lives")

LIVES_DIR.mkdir(exist_ok=True)


def fetch_lives():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    print("---->Start live fetching")

    try:
        live_matches = get_live_matches()
        if not live_matches:
            print("No live matches now → skipping API call")
            return False
    
        r = httpx.get(
            API_URL,
            headers=headers,
            timeout=20,
        )

        r.raise_for_status()

        data = r.json()  # <- list of leagues

        for league in data:
            league_key = league.get("league_key")

            if not league_key:
                print("⚠️ Skipping league without key")
                continue

            file_path = LIVES_DIR / f"{league_key}.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(league, f, ensure_ascii=False, indent=2)

            print(f"✅ Saved {file_path}")
        
        print("---->Done live fetching")

        return data

    except httpx.HTTPError as e:
        print("❌ HTTP error while fetching lives:", e)
        return []

# Scan /fixtures and detect live matches
def get_live_matches(fixtures_folder="fixtures"):
    live_matches = []

    for file in os.listdir(fixtures_folder):
        try:
            if not file.endswith(".json"):
                continue

            path = os.path.join(fixtures_folder, file)

            with open(path, "r", encoding="utf-8") as f:
                matches = json.load(f)
            
            fixtures = matches["matches"]
            for m in fixtures:
                if is_match_live(m["event_date"], m["event_time"]):
                    live_matches.append(m)
        except:
            continue

    return live_matches


# detect if match is “live window”
def is_match_live(event_date: str, event_time: str) -> bool:
    match_start = datetime.fromisoformat(f"{event_date} {event_time}")
    match_end = match_start + timedelta(minutes=120)
    now = datetime.utcnow()

    return match_start <= now <= match_end