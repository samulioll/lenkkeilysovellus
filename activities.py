from app import app
from db import db
from flask import session
from sqlalchemy import text
import datetime

def add_activity(form):
    try:
        parts = form["time"].split(":")
        time = int(parts[2]) + (60 * int(parts[1])) + (3600 * int(parts[0]))
        sql = text("INSERT INTO activities (user_id, sport_id, route_id, duration, date) VALUES (:user_id, :sport_id, :route_id, :duration, :date)")
        db.session.execute(sql, {"user_id":int(session["user_id"]), "sport_id":int(form["sport"]), "route_id":int(form["route"]), "duration":time, "date":str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
        db.session.commit()
        return True
    except:
        return False
