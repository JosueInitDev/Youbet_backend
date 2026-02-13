# Youbet backend
# App created by Darius
# All rights reserved jose.init.dev@...

from fastapi import FastAPI
from db import Base, engine
from routes import users, fixtures, lives, bets, leagues
from cron.fetch_fixtures import run as fetch_fixtures
from cron.fetch_lives import fetch_lives
from apscheduler.schedulers.background import BackgroundScheduler
from cron.settle_pending_bets import settle_pending_bets
import asyncio

app = FastAPI(title="Youbet Backend", redirect_slashes=False)

Base.metadata.create_all(bind=engine) # Create DB tables

app.include_router(users.router)
app.include_router(fixtures.router)
app.include_router(lives.router)
app.include_router(bets.router)
app.include_router(leagues.router)

# --- Startup Event ---
scheduler = BackgroundScheduler()
@app.on_event("startup")
async def startup_event():
    print("[STARTUP] Fetching fixtures and live matches once...")
    loop = asyncio.get_event_loop()
    
    try:
        await loop.run_in_executor(None, fetch_fixtures)
    except Exception as e:
        print(f"[ERROR] fetch_fixtures failed: {e}")

    try:
        await loop.run_in_executor(None, fetch_lives)
    except Exception as e:
        print(f"[ERROR] fetch_lives failed: {e}")

    print("[STARTUP] Done fetching initial data.")

    scheduler.add_job(fetch_lives, "interval", minutes=1, id="job1")
    scheduler.add_job(fetch_fixtures, "interval", minutes=1440, id="job2")
    scheduler.add_job(settle_pending_bets, trigger="cron", hour=19, minute=0, id="job3")
    scheduler.add_job(settle_pending_bets, trigger="cron", hour=23, minute=0, id="job4")
    scheduler.start()
