from app import app
from db import db
from flask import session
from sqlalchemy import text
import datetime
import services.handlers.users as users

def add_comment(form):
    try:
        sql = text("""INSERT INTO comments 
                      (activity_id, user_id, content, date, seen, visible)
                      VALUES
                      (:activity_id, :user_id, :content, :date, FALSE, TRUE)""")
        db.session.execute(sql, {"activity_id": form["activity"],
                                 "user_id": session["user_id"],
                                 "content": form["content"],
                                 "date": str(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
    except:
        return (False, "error in adding comment")
