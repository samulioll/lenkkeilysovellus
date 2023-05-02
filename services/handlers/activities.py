import datetime
from . import comments, users, sports, activity_routes
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
            if comments.add_comment(form):
                return (True, "")
            else:
                raise ValueError
        else:
            return (False, "Invalid time")
    except:
        return (False, "error in adding activity")

def add_comment(form):
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
        sport = sports.get_sport(activity.sport_id)
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
        sport = sports.get_sport(activity.sport_id)
        activity_info = activity_routes.get_activity_route(activity.route_id)
        duration_str = tools.format_time(activity.duration)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        comment_count = comments.get_comment_count(activity.id)
        activities.append([activity.id, username, sport, activity_info[0], activity_info[1], 
                           duration_str, date_str, comment_count])
    return activities

