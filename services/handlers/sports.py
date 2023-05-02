import secrets
from app import app
from db import db
from flask import session
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

def get_sport(sport_id):
    try:
        sport_sql = text("SELECT name FROM sports WHERE id=:sport_id")
        sport_fetch = db.session.execute(sport_sql, {"sport_id":sport_id})
        sport = sport_fetch.fetchone()[0]
        return sport
    except:
        return False