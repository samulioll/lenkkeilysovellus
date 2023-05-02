from app import app
from db import db
from flask import session
from sqlalchemy import text

def get_activity_routes():
    try:
        result = db.session.execute(text("SELECT * FROM routes"))
        return result.fetchall()
    except:
        return False

def get_activity_route(route_id):
    try:
        sql = text("SELECT name, length from routes WHERE id=:route_id")
        fetch = db.session.execute(sql, {"route_id":route_id})
        info = fetch.fetchone()
        route = info[0]
        length = str(info[1]) + "km"
        return (route, length)
    except:
        return False