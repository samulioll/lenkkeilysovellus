from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def front_page():
    session["username_error"] = False
    session["password_error"] = False
    return render_template("front_page.html")

@app.route("/login_view")
def login_view():
    return render_template("login_view.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM Users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        session["attempted_user"] = username
        session["username_error"] = True
        session["password_error"] = False
        return redirect("/login_view")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            print("Logged in as", username)
            session["username"] = username
            session["password_error"] = False
            session["username_error"] = False
            return redirect("/user_dashboard")
        else:
            session["password_error"] = True
            session["username_error"] = False
            return redirect("/login_view")
        
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register_view")
def register_view():
    return render_template("register_view.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    sql = text("SELECT username FROM Users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user:
        session["username_error"] = True
        session["attempted_user"] = username
        session["password_error"] = False
        return redirect("/register_view")
    if password1 != password2:
        session["password_error"] = True
        session["username_error"] = False
        return redirect("/register_view") 
    session["password_error"] = False
    session["username_error"] = False
    hash_value = generate_password_hash(password1)
    sql = text("INSERT INTO Users (username, password) VALUES (:username, :password)")
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    print("Account created")
    session["username"] = username
    return redirect("/user_dashboard")

@app.route("/user_dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")



