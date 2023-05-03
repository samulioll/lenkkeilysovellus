import secrets
from app import app
from db import db
from . import comments
from flask import session
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            session["unseen_comments"] = comments.get_unseen_count()
            return True
        else:
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
    result = db.session.execute(sql, {"username":username})
    username_taken = result.fetchone()
    if username_taken:
        return False
    else:
        hash_value = generate_password_hash(password)
        try:
            sql = text("INSERT INTO users (username, password) VALUES(:username, :password)")
            db.session.execute(sql, {"username":username, "password":hash_value})
            db.session.commit()
            return login(username, password)
        except:
            return False
        
def get_username(user_id):
    try:
        username_sql = text("SELECT username FROM users WHERE id=:user_id")
        username_fetch = db.session.execute(username_sql, {"user_id":user_id})
        username = username_fetch.fetchone()[0]
        return username
    except:
        return False
