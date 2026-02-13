from db import SessionLocal
from models import Bet
from datetime import datetime, timedelta
import json
import os

FIXTURES_PATH = "fixtures"
        
def settle_pending_bets():
    db = SessionLocal()
    print("[Start] Pending bets settled.")

    # Get all pending bets
    try:
        pending_bets = db.query(Bet).filter(Bet.win == None).all()
    finally:
        db.close()

    if not pending_bets:
        print("No pending bets")
        return

    # Load all fixtures
    fixtures_data = {}
    for file in os.listdir(FIXTURES_PATH):
        if file.endswith(".json"):
            with open(os.path.join(FIXTURES_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                for match in data.get("matches", []):
                    fixtures_data[match["event_key"]] = match

    # Loop over each pending bet
    for bet in pending_bets:
        match_key = json.loads(bet.match_data)["event_key"] if isinstance(bet.match_data, str) else bet.match_data["event_key"]
        match = fixtures_data.get(match_key)
        if not match:
            # print(f"No fixture found for bet {bet.id}")
            continue

        # match datetime + 100 minutes
        match_datetime = datetime.strptime(f"{match['event_date']} {match['event_time']}", "%Y-%m-%d %H:%M")
        match_end_time = match_datetime + timedelta(minutes=100)

        # Only settle if match is over
        if datetime.utcnow() < match_end_time:
            continue

        # Determine if bet won
        bet_outcome = bet.bet.lower()
        result_home = match.get("event_home_final_score")
        result_away = match.get("event_away_final_score")

        # Skip if match result not available yet
        if result_home is None or result_away is None:
            continue

        # Simple example for match_odds
        win = False
        if bet.bet_type == "match_odds":
            if bet_outcome == "home" and result_home > result_away:
                win = True
            elif bet_outcome == "away" and result_away > result_home:
                win = True
            elif bet_outcome == "draw" and result_home == result_away:
                win = True

        # Other bet types can be added here (double_chance, both_teams_to_score, correct_score, etc.)

        bet.win = win
        bet.updatedAt = datetime.utcnow()
        db.add(bet)

    db.commit()
    print("[Done] Pending bets settled.")