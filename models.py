from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    username = Column(String)
    balance = Column(Float, default=0)

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    bet_type = Column(String)

    match_data = Column(Text)
    selections = Column(Text)

    selected_outcome = Column(String)

    stake = Column(Float)

    win = Column(Boolean, nullable=True)

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)
