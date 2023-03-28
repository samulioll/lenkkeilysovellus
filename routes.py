from app import app
import activities, users
from flask import render_template, redirect, request, session


@app.route("/")
def front_page():
    return render_template("front_page.html", user_id=users.user_id())

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/user_dashboard.html")
        else:
            return render_template("login.html", error_message="Incorrect username or password")

@app.route("/logout")
def logout():
    #users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("register.html", error_message="Passwords don't match")
        if users.register(username, password1):
            return redirect("/user_dashboard")
        else:
            return render_template("register.html", error_message="Username is already in use")
