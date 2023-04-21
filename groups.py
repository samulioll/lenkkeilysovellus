from app import app
from db import db
from flask import session
from sqlalchemy import text

def join_group(form):
    try:
        sql = text("INSERT INTO groupmembers (user_id, group_id) VALUES (:user_id, :group_id)")
        db.session.execute(sql, {"user_id":int(session["user_id"]), "group_id":int(form["groups"])})
        db.session.commit()
        return True
    except:
        return False

def leave_group():
    pass

def user_groups_overview():
    sql = text("SELECT G.name FROM groups G, groupmembers M WHERE G.id=M.group_id AND M.user_id=:user_id")
    result = db.session.execute(sql, {"user_id":session["user_id"]})
    return result.fetchall()

def get_groups():
    result = db.session.execute(text("SELECT * FROM groups"))
    return result.fetchall()
