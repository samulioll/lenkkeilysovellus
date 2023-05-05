import secrets
from flask import session
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from services import tools


def login(username, password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        return False
    if check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        session["unseen_comments"] = get_unseen_count()
        return True
    return False


def user_id():
    return session.get("user.id", 0)


def logout():
    del session["user_id"]
    del session["username"]
    del session["csrf_token"]
    del session["unseen_comments"]


def register(username, password):
    sql = text("SELECT id FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    username_taken = result.fetchone()
    if username_taken:
        return False
    hash_value = generate_password_hash(password)
    sql = text("""INSERT INTO users
                    (username, password, public) 
                    VALUES 
                    (:username, :password, TRUE)""")
    db.session.execute(sql, {"username": username, "password": hash_value})
    db.session.commit()
    return login(username, password)


def get_username(user_id):
    sql = text("SELECT username FROM users WHERE id=:user_id")
    result = db.session.execute(sql, {"user_id": user_id})
    if result:
        return result.fetchone()[0]
    return False


def is_public(user_id):
    sql = text("""SELECT public
                  FROM users
                  WHERE id=:user_id""")
    result = db.session.execute(sql, {"user_id": user_id})
    if result:
        return result.fetchone()[0]
    return False


def make_public():
    sql = text("""UPDATE users
                    SET public=TRUE
                    WHERE id=:user_id""")
    db.session.execute(sql, {"user_id": session["user_id"]})
    db.session.commit()
    return True


def make_private():
    sql = text("""UPDATE users
                    SET public=FALSE
                    WHERE id=:user_id""")
    db.session.execute(sql, {"user_id": session["user_id"]})
    db.session.commit()
    return True


def user_overview(user_id):
    total_dist = get_total_distance(user_id)
    walked = get_distance_walked(user_id)
    ran = get_distance_ran(user_id)
    cycled = get_distance_cycled(user_id)
    total_time = tools.format_time(get_total_time(user_id))
    return (total_dist, walked, ran, cycled, total_time)


def get_total_distance(user_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE user_id=:user_id)""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchone()[0]


def get_distance_walked(user_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE user_id=:user_id)
                  AND A.sport_id=1""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchone()[0]


def get_distance_ran(user_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE user_id=:user_id)
                  AND A.sport_id=2""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchone()[0]


def get_distance_cycled(user_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R 
                  ON A.route_id=R.id 
                  WHERE A.user_id IN 
                  (SELECT user_id FROM groupmembers WHERE user_id=:user_id)
                  AND A.sport_id=3""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchone()[0]


def get_total_time(user_id):
    sql = text("""SELECT SUM(duration)
                  FROM activities
                  WHERE user_id IN 
                  (SELECT user_id FROM groupmembers WHERE user_id=:user_id)""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchone()[0]


def get_unseen_count():
    sql = text("""SELECT COUNT(C.id)
                  FROM comments C, activities A
                  WHERE C.activity_id=A.id AND A.user_id=:user_id
                  AND C.visible=TRUE AND C.seen=FALSE""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return result.fetchone()[0]
