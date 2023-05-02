import datetime
from app import app
from db import db
from flask import session
from sqlalchemy import text
from . import users

def add_comment(form):
    sql = text("""INSERT INTO comments 
                    (activity_id, user_id, content, date, seen, visible)
                    VALUES
                    (:activity_id, :user_id, :content, :date, FALSE, TRUE)""")
    db.session.execute(sql, {"activity_id": form["activity_id"],
                                "user_id": session["user_id"],
                                "content": form["comment"],
                                "date": str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
    db.session.commit()
    return (True, "")


def get_comments(activity_id):
    try:
        sql = text("""SELECT *
                        FROM comments
                        WHERE activity_id=:activity_id""")
        result = db.session.execute(sql, {"activity_id": activity_id})
        return result.fetchall()
    except:
        return False

def get_comment_count(activity_id):
    try:
        sql = text("""SELECT COUNT(id)
                        FROM comments
                        WHERE activity_id=:activity_id""")
        result = db.session.execute(sql, {"activity_id": activity_id})
        return result.fetchone()[0]
    except:
        return False

