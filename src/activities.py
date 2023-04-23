from app import app
from db import db
from flask import session
from sqlalchemy import text
import datetime
import users

def add_activity(form):
    try:
        parts = form["time"].split(":")
        if check_valid_time(parts):
            time = int(parts[2]) + (60 * int(parts[1])) + (3600 * int(parts[0]))
            sql = text("INSERT INTO activities (user_id, sport_id, route_id, duration, date, visible) VALUES (:user_id, :sport_id, :route_id, :duration, :date, TRUE)")
            db.session.execute(sql, {"user_id":int(session["user_id"]), "sport_id":int(form["sport"]), "route_id":int(form["routes"]), "duration":time, "date":str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
            db.session.commit()
            return (True, "")
        else:
            return (False, "Invalid time")
    except:
        return (False, "error in adding activity")

def check_valid_time(parts: list):
    for part in parts:
        if len(part) > 2 or int(part) > 59:
            return False
    return True
    
def user_activities_overview():
    sql = text("SELECT * FROM activities WHERE user_id=:user_id ORDER BY id DESC LIMIT 5")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def user_groups_activities_overview():
    sql = text("SELECT DISTINCT A.* FROM activities A, groupmembers G WHERE A.visible=TRUE AND A.user_id=G.user_id AND G.user_id IN (SELECT DISTINCT U.id FROM users U, groupmembers G WHERE U.id=G.user_id AND G.group_id IN (SELECT DISTINCT group_id FROM groupmembers WHERE user_id=:user_id)) ORDER BY A.id DESC LIMIT 5")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def all_user_activities():
    sql = text("SELECT * FROM activities WHERE user_id=:user_id ORDER BY id DESC")
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

def format_group_activities_for_overview(list):
    activities = []
    for activity in list:
        username_sql = text("SELECT username FROM users WHERE id=:user_id")
        username_fetch = db.session.execute(username_sql, {"user_id":activity.user_id})
        username = username_fetch.fetchone()[0]
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
        activities.append([username, sport, activity_route, activity_length, duration_str, date_str])
    return activities


