from app import app
from db import db
from flask import session
from sqlalchemy import text
from services import tools

def join_group(form):
    try:
        sql = text("""INSERT INTO groupmembers 
                      (user_id, group_id, visible) 
                      VALUES (:user_id, :group_id, TRUE)""")
        db.session.execute(sql, {"user_id":int(session["user_id"]), 
                                 "group_id":int(form["groups"])})
        db.session.commit()
        return True
    except:
        return False

def leave_group(form):
    try:
        sql = text("""UPDATE groupmembers 
                      SET visible=FALSE 
                      WHERE user_id=:user_id AND group_id=:group_id""")
        db.session.execute(sql, {"user_id":session["user_id"], 
                                 "group_id":form["groups"]})
        db.session.commit()
        return True
    except:
        return False

def user_groups_overview():
    sql = text("""SELECT G.name, G.id 
                  FROM groups G, groupmembers M 
                  WHERE G.id=M.group_id AND M.user_id=:user_id AND M.visible=TRUE""")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def get_groups():
    result = db.session.execute(text("SELECT * FROM groups WHERE visible=TRUE"))
    return result.fetchall()

def group_overview(group_id):
    total_dist = get_total_distance(group_id)
    walked = get_distance_walked(group_id)
    ran = get_distance_ran(group_id)
    cycled = get_distance_cycled(group_id)
    total_time = tools.format_time(get_total_time(group_id))
    return (total_dist, walked, ran, cycled, total_time)

def get_members(group_id):
    sql = text("""SELECT U.id, U.username 
                  FROM users U, groupmembers G 
                  WHERE U.id=G.user_id and G.group_id=:group_id AND G.visible=TRUE""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchall()

def get_name(group_id):
    sql = text("SELECT name FROM groups WHERE id=:group_id")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]

def get_total_distance(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]

def get_distance_walked(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=1""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]

def get_distance_ran(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=2""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]

def get_distance_cycled(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=3""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]

def get_total_time(group_id):
    sql = text("""SELECT SUM(duration)
                  FROM activities
                  WHERE user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)""")
    result = db.session.execute(sql, {"group_id":group_id})
    return result.fetchone()[0]
