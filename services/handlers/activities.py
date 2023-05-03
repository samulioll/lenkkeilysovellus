import datetime
from . import comments, users, activity_routes
from app import app
from db import db
from flask import session
from sqlalchemy import text
from services import tools

def add_activity(form):
    try:
        time = tools.return_valid_time(form["time"])
        if time:
            sql = text("""INSERT INTO activities 
                          (user_id, sport_id, route_id, duration, date, visible) 
                          VALUES 
                          (:user_id, :sport_id, :route_id, :duration, :date, TRUE)""")
            db.session.execute(sql, {"user_id":int(session["user_id"]), 
                                     "sport_id":int(form["sport"]), 
                                     "route_id":int(form["routes"]), 
                                     "duration":time, 
                                     "date":str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
            db.session.commit()
            #if comments.add_comment(form):
            return (True, "")
            #else:
            #    raise ValueError
        else:
            return (False, "Invalid time")
    except:
        return (False, "error in adding activity")

def add_comment(form):
    if len(form["comment"]) < 1:
        return True
    try:
        sql = text("""INSERT INTO comments 
                      (activity_id, user_id, content, date, visible) 
                      VALUES 
                      (:activity_id, :user_id, :content, :date, TRUE)""")
        act_id_fetch = db.session.execute(text("SELECT COUNT(*) FROM activities"))
        activity_id= act_id_fetch.fetchone()[0]
        db.session.execute(sql, {"activity_id":int(activity_id), 
                                 "user_id":int(session["user_id"]), 
                                 "content":str(form["comment"]), 
                                 "date":str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
        db.session.commit()
        print("test")
        return True
    except:
        return False
    
def user_activities_overview():
    sql = text("""SELECT * 
                  FROM activities 
                  WHERE user_id=:user_id 
                  ORDER BY id DESC 
                  LIMIT 5""")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def user_groups_activities_overview():
    sql = text("""SELECT DISTINCT A.* 
                  FROM activities A, groupmembers G 
                  WHERE A.visible=TRUE AND A.user_id=G.user_id AND G.user_id IN 
                  (SELECT DISTINCT U.id FROM users U, groupmembers G WHERE U.id=G.user_id AND G.group_id IN 
                  (SELECT DISTINCT group_id FROM groupmembers WHERE user_id=:user_id)) 
                  ORDER BY A.id DESC 
                  LIMIT 5""")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def all_user_activities():
    sql = text("""SELECT * 
                  FROM activities 
                  WHERE user_id=:user_id 
                  ORDER BY id DESC""")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def all_user_group_activities():
    sql = text("""SELECT DISTINCT A.* 
                  FROM activities A, groupmembers G 
                  WHERE A.visible=TRUE AND A.user_id=G.user_id AND G.user_id IN 
                  (SELECT DISTINCT U.id FROM users U, groupmembers G WHERE U.id=G.user_id AND G.group_id IN 
                  (SELECT DISTINCT group_id FROM groupmembers WHERE user_id=:user_id)) 
                  ORDER BY A.id DESC""")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def format_activities_for_overview(list):
    activities = []
    for activity in list:
        sport = get_sport(activity.sport_id)
        activity_info = activity_routes.get_activity_route(activity.route_id)
        duration_str = tools.format_time(activity.duration)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        comment_count = comments.get_comment_count(activity.id)
        activities.append([activity.id, sport, activity_info[0], activity_info[1], 
                           duration_str, date_str, comment_count])
    return activities

def format_group_activities_for_overview(list):
    activities = []
    for activity in list:
        username = users.get_username(activity.user_id)
        sport = get_sport(activity.sport_id)
        activity_info = activity_routes.get_activity_route(activity.route_id)
        duration_str = tools.format_time(activity.duration)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        comment_count = comments.get_comment_count(activity.id)
        activities.append([activity.id, username, sport, activity_info[0], activity_info[1], 
                           duration_str, date_str, comment_count])
    return activities

def activity_info_short(activity_id):
    sql = text("""SELECT *
                  FROM activities 
                  WHERE id=:activity_id """)
    result = db.session.execute(sql, {"activity_id":activity_id})
    return format_activity_short(result.fetchone())

def format_activity_short(activity):
    sport = get_sport(activity.sport_id).capitalize()
    length = get_length(activity.route_id)
    parts = activity.date.split("_")
    date = parts[0]
    return sport + " | " + str(length) + "km | " + date

def get_sport(sport_id):
    sport_sql = text("SELECT name FROM sports WHERE id=:sport_id")
    sport_fetch = db.session.execute(sport_sql, {"sport_id":sport_id})
    sport = sport_fetch.fetchone()[0]
    return sport
    
def get_length(route_id):
    length_sql = text("""SELECT length 
                    FROM routes
                    WHERE id=:route_id""")
    length_fetch = db.session.execute(length_sql, {"route_id":route_id})
    length = length_fetch.fetchone()[0]
    return length
