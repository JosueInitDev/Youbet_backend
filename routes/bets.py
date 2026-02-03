from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Bet
from pydantic import BaseModel
import json

router = APIRouter(prefix="/bets", tags=["Bets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for the request body
class CreateBetBody(BaseModel):
    user_id: int
    bet_type: str
    match_data: dict
    selections: list
    selected_outcome: str
    stake: float


@router.post("")
def create_bet(body: CreateBetBody, db: Session = Depends(get_db)):
    """
    Create a new bet and return all bets for this user.
    All data comes from request JSON body.
    """
    # --- Create new bet ---
    bet = Bet(
        user_id=body.user_id,
        bet_type=body.bet_type,
        match_data=json.dumps(body.match_data),
        selections=json.dumps(body.selections),
        selected_outcome=body.selected_outcome,
        stake=body.stake
    )

    db.add(bet)
    db.commit()
    db.refresh(bet)

    # --- Fetch all bets for this user ---
    user_bets = db.query(Bet).filter(Bet.user_id == body.user_id).all()

    # Convert JSON strings back to dict for response
    result = []
    for b in user_bets:
        result.append({
            "id": b.id,
            "bet_type": b.bet_type,
            "match_data": json.loads(b.match_data),
            "selections": json.loads(b.selections),
            "selected_outcome": b.selected_outcome,
            "stake": b.stake,
            "win": b.win,
            "createdAt": b.createdAt,
            "updatedAt": b.updatedAt,
            "deletedAt": b.deletedAt
        })

    return {
        "success": True,
        "bet_id": bet.id,
        "user_bets": result
    }


@router.get("/user/{user_id}")
def get_user_bets(user_id: int, db: Session = Depends(get_db), limit: int = Query(100, le=100)):
    """
    Return up to `limit` bets for a user, ordered by createdAt descending.
    """
    bets = (
        db.query(Bet)
        .filter(Bet.user_id == user_id)
        .order_by(Bet.createdAt.desc())
        .limit(limit)
        .all()
    )

    result = []
    for b in bets:
        result.append({
            "id": b.id,
            "bet_type": b.bet_type,
            "match_data": json.loads(b.match_data),
            "selections": json.loads(b.selections),
            "selected_outcome": b.selected_outcome,
            "stake": b.stake,
            "win": b.win,
            "createdAt": b.createdAt,
            "updatedAt": b.updatedAt,
            "deletedAt": b.deletedAt
        })

    return result