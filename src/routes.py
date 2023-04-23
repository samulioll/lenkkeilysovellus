from app import app
import activities, users, activity_routes, groups
from flask import render_template, redirect, request, session


@app.route("/")
def front_page():
    return render_template("front_page.html", 
                           user_id=users.user_id()
                           )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/dashboard")
        else:
            return render_template("login.html", 
                                   error_message="Incorrect username or password"
                                   )

@app.route("/logout")
def logout():
    users.logout()
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
            return render_template("register.html", 
                                   error_message="Passwords don't match"
                                   )
        if users.register(username, password1):
            return redirect("/dashboard")
        else:
            return render_template("register.html", 
                                   error_message="Username is already in use"
                                   )

@app.route("/dashboard")
def dashboard():
    own_overview = activities.user_activities_overview()
    own_formatted = activities.format_activities_for_overview(own_overview)
    groups_overview = activities.user_groups_activities_overview()
    groups_formatted = activities.format_group_activities_for_overview(groups_overview)
    return render_template("dashboard.html", 
                           own_list=own_formatted,
                           groups_list = groups_formatted
                           )

@app.route("/all_activities")
def all_activities():
    activity_list = activities.all_user_activities()
    formatted = activities.format_activities_for_overview(activity_list)
    return render_template("all_activities.html", 
                           activity_list=formatted
                           )

@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "GET":
        return render_template("add_activity.html", 
                               route_list = activity_routes.get_activity_routes()
                               )
    elif request.method == "POST":
        success, message = activities.add_activity(request.form)
        if success:
            return redirect("/dashboard")
        else:
            return render_template("add_activity.html", 
                                   error_message=message
                                   )

@app.route("/community")
def community():
    return render_template(
        "community_page.html", 
        user_id=users.user_id(),
        user_groups=groups.user_groups_overview()
        )

@app.route("/join_group", methods=["GET", "POST"])
def join_group():
    if request.method == "GET":
        return render_template("join_group.html", 
                               group_list=groups.get_groups()
                               )
    elif request.method == "POST":
        if groups.join_group(request.form):
            return redirect("/community")
        else:
            return render_template("join_group.html", 
                                   group_list=groups.get_groups(), 
                                   error_message="Error in joining group"
                                   )
        
@app.route("/leave_group", methods=["GET", "POST"])
def leave_group():
    if request.method == "GET":
        return render_template("leave_group.html", 
                               group_list=groups.get_groups()
                               )
    elif request.method == "POST":
        if groups.leave_group(request.form):
            return redirect("/community")
        else:
            return render_template("leave_group.html", 
                                   group_list=groups.get_groups(), 
                                   error_message="Error in leaving group"
                                   )
        
@app.route("/group_overview", methods=["GET", "POST"])
def group_overview():
    if request.method == "POST":
        return render_template("group_overview.html", 
                               group_members=groups.group_overview(request.form), 
                               group_name=groups.get_name(request.form)
                               )
