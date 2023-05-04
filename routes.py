from app import app
from services.handlers import activities, users, activity_routes, groups, comments
from flask import render_template, redirect, request, session, abort, url_for


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

@app.route("/all_group_activities")
def all_group_activities():
    activity_list = activities.all_user_group_activities()
    formatted = activities.format_group_activities_for_overview(activity_list)
    return render_template("all_group_activities.html", 
                           activity_list=formatted
                           )

@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "GET":
        return render_template("add_activity.html", 
                               route_list = activity_routes.get_activity_routes()
                               )
    elif request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        success, error_msg = activities.add_activity(request.form)
        if success:
            return redirect("/dashboard")
        else:
            return render_template("add_activity.html",
                                   route_list = activity_routes.get_activity_routes(),
                                   error_message=error_msg
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
        if session["csrf_token"] != request.form["csrf_token"]:
                    abort(403)
        group_id = request.form["groups"]
        if groups.join_group(group_id):
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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        group_id = request.form["groups"]
        user_id = request.form["user_id"]
        if groups.leave_group(group_id, user_id):
            return redirect("/community")
        else:
            return render_template("leave_group.html", 
                                   group_list=groups.get_groups(), 
                                   error_message="Error in leaving group"
                                   )

@app.route("/create_group", methods=["GET", "POST"])
def create_group():
    if request.method == "GET":
        return render_template("create_group.html")
    else:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        success, error_msg, group_id = groups.create_group(request.form)
        print(group_id)
        if success:
            groups.join_group_owner(group_id)
            return redirect("/group/"+str(group_id))
        else:
            return render_template("create_group.html",
                                   error_message=error_msg)

@app.route("/group/<int:group_id>", methods=["GET", "POST"])
def group(group_id):
    if request.method == "GET":
        g_members = groups.get_normal_members(group_id)
        g_name = groups.get_name(group_id)
        g_overview = groups.group_overview(group_id)
        g_owner = groups.get_owner(group_id)
        g_admins = groups.get_admins(group_id)
        g_admin_right = True if session["username"] in g_admins[0] else False
        return render_template("group_overview.html", 
                               group_members=g_members, 
                               group_name=g_name,
                               group_overview = g_overview,
                               group_owner=g_owner,
                               group_admins=g_admins,
                               admin_rights=g_admin_right,
                               group_id=group_id)

@app.route("/group/<int:group_id>/manage", methods=["GET", "POST"])
def manage_group(group_id):
    if request.method == "GET":
        g_members = groups.get_normal_members(group_id)
        g_name = groups.get_name(group_id)
        g_owner = groups.get_owner(group_id)
        g_admins = groups.get_admins(group_id)
        return render_template("group_manager.html",
                               group_name=g_name,
                               group_members=g_members,
                               group_owner=g_owner,
                               group_admins=g_admins,
                               group_id=group_id)

@app.route("/activity/<int:activity_id>/activity_comments", methods=["GET", "POST"])
def activity_comments(activity_id):
    if request.method == "GET":
        return render_template("activity_comments.html",
                               comment_list=comments.get_comments(activity_id),
                               activity_id=activity_id,
                               activity_info = activities.activity_info_short(activity_id))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if request.form["action"] == "delete":
            success, error_msg = comments.delete_comment(request.form)
            if success:
                return render_template("activity_comments.html",
                                    comment_list=comments.get_comments(activity_id),
                                    activity_id=activity_id,
                                    activity_info = activities.activity_info_short(activity_id))
            else:
                return render_template("activity_comments.html",
                                    comment_list=comments.get_comments(activity_id),
                                    activity_id=activity_id,
                                    error_message=error_msg)
        else:
            success, error_msg = comments.add_comment(request.form)
            if success:
                return render_template("activity_comments.html",
                                    comment_list=comments.get_comments(activity_id),
                                    activity_id=activity_id,
                                    activity_info = activities.activity_info_short(activity_id))
            else:
                return render_template("activity_comments.html",
                                    comment_list=comments.get_comments(activity_id),
                                    activity_id=activity_id,
                                    error_message=error_msg)

@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def user_overview(user_id):
    if request.method == "GET":
        u_username = users.get_username(user_id)
        if users.is_public(user_id) or user_id == session["user_id"]:
            u_overview = users.user_overview(user_id)
            u_public = users.is_public(user_id)
            return render_template("user_overview.html",
                                user_id=user_id,
                                user_public = u_public,
                                username=u_username,
                                user_overview=u_overview)
        else:
            return render_template("user_private.html",
                                   username=u_username)
    else:
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if request.form["make_profile"] == "public":
            users.make_public()
            return redirect("/user/"+str(user_id))
        else:
            users.make_private()
            return redirect("/user/"+str(user_id))

@app.route("/user/<int:user_id>/new_comments")
def new_comments(user_id):
    if session["user_id"] == user_id:
        c_list=comments.get_unseen_comments()
        if c_list:
            if comments.mark_as_read():
                session["unseen_comments"] = comments.get_unseen_count()
        return render_template("new_comments.html",
                               comment_list= c_list)
    else:
        return redirect("/")

@app.route("/leaderboard/<int:choice>")
def leaderboard(choice):
    if choice == 1:
        return render_template("leaderboard_users.html",
                               u_list = activities.user_leaderboard())
    else:
        return render_template("leaderboard_groups.html")