from app import app
from db import db
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
            return True
        else:
            return False
        
def user_id():
    return session.get("user.id", 0)
        
def logout():
    del session["user_id"]
        
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
        except:
            return False
        return login(username, password)