from app import app
from db import db
from flask import session
from sqlalchemy import text
import datetime
import services.handlers.users as users

def get_activity_routes():
    result = db.session.execute(text("SELECT * FROM routes"))
    return result.fetchall()