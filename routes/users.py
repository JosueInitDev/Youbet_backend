from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User, Bet
from auth import generate_token, generate_username
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from sqlalchemy import desc

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1️⃣ Auto create user
@router.post("/auto-create")
def auto_create_user(db: Session = Depends(get_db)):

    user = User(
        token=generate_token(),
        username=generate_username(),
        balance=1000,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "token": user.token,
        "username": user.username,
        "balance": user.balance
    }


# 4️⃣ Fetch user by token
@router.get("/me/{token}")
def get_user(token: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.token == token).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user


# 5️⃣ Update user
@router.patch("/me/{token}")
def update_user(token: str, balance: float, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.token == token).first()

    if not user:
        raise HTTPException(404)

    user.balance = balance
    user.updatedAt = datetime.utcnow()

    db.commit()

    return {"success": True}


@router.get("/list/{token}")
def list_users(token: str, db: Session = Depends(get_db)):
    require_admin(token)
    
    users = (
        db.query(User)
        .filter(User.deletedAt.is_(None))
        .order_by(desc(User.createdAt))
        .limit(1000)
        .all()
    )

    result = []

    for user in users:
        # Get latest 50 bets for each user
        bets = (
            db.query(Bet)
            .filter(
                Bet.user_id == user.id,
                Bet.deletedAt.is_(None)
            )
            .order_by(desc(Bet.createdAt))
            .limit(30)
            .all()
        )

        formatted_bets = []

        for bet in bets:
            formatted_bets.append({
                "id": bet.id,
                "bet_type": bet.bet_type,
                "match_data": json.loads(bet.match_data) if bet.match_data else None,
                "bet": bet.selected_outcome,
                "stake": bet.stake,
                "win": bet.win,
                "createdAt": bet.createdAt,
            })

        result.append({
            "id": user.id,
            "username": user.username,
            "balance": user.balance,
            "createdAt": user.createdAt,
            "updatedAt": user.updatedAt,
            "bets": formatted_bets,
        })
    
    return result


def require_admin(token: str | None):
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized :1")

