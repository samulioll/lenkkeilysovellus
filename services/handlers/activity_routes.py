from sqlalchemy import text
from db import db


def get_activity_routes():
    result = db.session.execute(text("SELECT * FROM routes"))
    return result.fetchall()


def get_activity_route(route_id):
    sql = text("SELECT name, length from routes WHERE id=:route_id")
    fetch = db.session.execute(sql, {"route_id": route_id})
    info = fetch.fetchone()
    if info:
        route = info[0]
        length = str(info[1]) + "km"
        return (route, length)
    return False
