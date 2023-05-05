import datetime
from flask import session
from sqlalchemy import text
from db import db
from services import tools
from .users import get_username
from .activities import activity_info_short


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


def delete_comment(form):
    sql = text("""UPDATE comments
                    SET visible=False
                    WHERE id=:comment_id""")
    db.session.execute(sql, {"comment_id": form["comment_id"]})
    db.session.commit()
    return (True, "")


def get_comments(activity_id):
    sql = text("""SELECT id, activity_id, user_id, content,
                  date, seen, visible
                  FROM comments
                  WHERE activity_id=:activity_id AND visible=TRUE
                  ORDER BY id DESC""")
    result = db.session.execute(sql, {"activity_id": activity_id})
    if result:
        return format_comments(result.fetchall())
    return False


def format_comments(all_comments):
    comment_list = []
    for comment in all_comments:
        author = get_username(comment.user_id)
        content = comment.content
        date = tools.format_date(comment.date)
        comment_list.append(
            (comment.user_id, author, content, date, comment.id))
    return comment_list


def format_new_comments(all_comments):
    comment_list = []
    for comment in all_comments:
        author = get_username(comment.user_id)
        content = comment.content
        date = tools.format_date(comment.date)
        activity_info = activity_info_short(comment.activity_id)
        comment_list.append((comment.user_id, author, content,
                            date, activity_info, comment.activity_id))
    return comment_list


def get_unseen_comments():
    sql = text("""SELECT C.id, C.activity_id, C.user_id, C.content,
                  C.date, C.seen, C.visible
                  FROM comments C, activities A
                  WHERE C.activity_id=A.id AND A.user_id=:user_id
                  AND C.visible=TRUE AND C.seen=FALSE""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return format_new_comments(result.fetchall())


def mark_as_read():
    sql = text("""UPDATE comments
                    SET seen=TRUE
                    WHERE activity_id IN
                    (SELECT id FROM activities WHERE user_id=:user_id)""")
    db.session.execute(sql, {"user_id": session["user_id"]})
    db.session.commit()
    return True
