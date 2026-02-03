from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User
from auth import generate_token, generate_username
from datetime import datetime

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
