from app import app
from db import db
from flask import session
from sqlalchemy import text
import datetime
import users

def add_activity(form):
    try:
        parts = form["time"].split(":")
        time = int(parts[2]) + (60 * int(parts[1])) + (3600 * int(parts[0]))
        sql = text("INSERT INTO activities (user_id, sport_id, route_id, duration, date) VALUES (:user_id, :sport_id, :route_id, :duration, :date)")
        db.session.execute(sql, {"user_id":int(session["user_id"]), "sport_id":int(form["sport"]), "route_id":int(form["routes"]), "duration":time, "date":str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
        db.session.commit()
        return True
    except:
        return False
    
def user_activities_overview():
    sql = text("SELECT * FROM activities WHERE user_id=:user_id")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def format_activities_for_overview(list):
    activities = []
    for activity in list:
        sport_sql = text("SELECT name FROM sports WHERE id=:sport_id")
        sport_fetch = db.session.execute(sport_sql, {"sport_id":activity.sport_id})
        sport = sport_fetch.fetchone()[0]
        act_sql = text("SELECT name, length from routes WHERE id=:route_id")
        act_fetch = db.session.execute(act_sql, {"route_id":activity.route_id})
        activity_info = act_fetch.fetchone()
        activity_route = activity_info[0]
        activity_length = str(activity_info[1]) + "km"
        hours = activity.duration // 3600
        mins = (activity.duration % 3600) // 60
        secs = (activity.duration % 3600) % 60
        duration_str = str(hours) + ":" + str(mins) + ":" + str(secs)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        activities.append([sport, activity_route, activity_length, duration_str, date_str])
    return activities


