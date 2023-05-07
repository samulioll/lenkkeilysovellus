from flask import render_template, redirect, request, session
from app import app
from services import tools
from services.handlers import activities, users, activity_routes, groups, comments


@app.route("/")
def front_page():
    user_id=users.user_id()
    acts = len(activities.user_activities_overview(user_id))
    return render_template("front_page.html",
                           user_id=user_id,
                           acts=acts
                           )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    if users.login(username, password):
        return redirect("/dashboard")
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
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return render_template("register.html",
                                error_message="Passwords don't match"
                                )
    if users.register(username, password1):
        return redirect("/dashboard")
    return render_template("register.html",
                            error_message="Username is already in use"
                            )


@app.route("/dashboard")
def dashboard():
    own_overview = activities.user_activities_overview(session["user_id"])
    own_formatted = activities.format_activities_for_overview(own_overview)
    groups_overview = activities.user_groups_activities_overview()
    groups_formatted = activities.format_group_activities_for_overview(
        groups_overview)
    return render_template("dashboard.html",
                           own_list=own_formatted,
                           groups_list=groups_formatted
                           )


@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "GET":
        return render_template("add_activity.html",
                               route_list=activity_routes.get_activity_routes()
                               )
    tools.verify_csrf(session["csrf_token"])
    success, error_msg = activities.add_activity(request.form)
    if success:
        return redirect("/dashboard")
    return render_template("add_activity.html",
                            route_list=activity_routes.get_activity_routes(),
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
    tools.verify_csrf(session["csrf_token"])
    group_id = request.form["groups"]
    if groups.join_group(group_id):
        return redirect("/community")
    return render_template("join_group.html",
                            group_list=groups.get_groups(),
                            error_message="Error in joining group"
                            )


@app.route("/leave_group", methods=["GET", "POST"])
def leave_group():
    if request.method == "GET":
        return render_template("leave_group.html",
                               group_list=groups.get_user_groups()
                               )
    tools.verify_csrf(session["csrf_token"])
    group_id = request.form["groups"]
    user_id = request.form["user_id"]
    if session["username"] in groups.get_owner(group_id):
        next_owner = groups.get_next_owner(group_id)
        if next_owner:
            groups.make_owner(group_id, next_owner)
        groups.delete_group(group_id)
    if groups.leave_group(group_id, user_id):
        return redirect("/community")
    return render_template("leave_group.html",
                            group_list=groups.get_groups(),
                            error_message="Error in leaving group"
                            )


@app.route("/remove_from_group", methods=["POST"])
def remove_from_group():
    tools.verify_csrf(session["csrf_token"])
    group_id = request.form["groups"]
    user_id = request.form["user_id"]
    if groups.leave_group(group_id, user_id):
        return redirect("/group/"+str(group_id)+"/manage")
    return render_template("leave_group.html",
                            group_list=groups.get_groups(),
                            error_message="Error in leaving group"
                            )


@app.route("/make_admin", methods=["POST"])
def make_admin():
    tools.verify_csrf(session["csrf_token"])
    group_id = request.form["groups"]
    user_id = request.form["user_id"]
    if groups.make_admin(group_id, user_id):
        return redirect("/group/"+str(group_id)+"/manage")
    return render_template("leave_group.html",
                            group_list=groups.get_groups(),
                            error_message="Error in making admin"
                            )


@app.route("/demote_admin", methods=["POST"])
def demote_admin():
    tools.verify_csrf(session["csrf_token"])
    group_id = request.form["groups"]
    user_id = request.form["user_id"]
    if groups.demote_admin(group_id, user_id):
        return redirect("/group/"+str(group_id)+"/manage")
    return render_template("leave_group.html",
                            group_list=groups.get_groups(),
                            error_message="Error in demoting admin"
                            )


@app.route("/create_group", methods=["GET", "POST"])
def create_group():
    if request.method == "GET":
        return render_template("create_group.html")
    tools.verify_csrf(session["csrf_token"])
    success, error_msg, group_id = groups.create_group(request.form)
    if success:
        groups.join_group_owner(group_id)
        return redirect("/group/"+str(group_id))
    return render_template("create_group.html",
                            error_message=error_msg)


@app.route("/delete_group", methods=["POST"])
def delete_group():
    tools.verify_csrf(session["csrf_token"])
    groups.delete_group(request.form["group_id"])
    return redirect("/community")


@app.route("/group/<int:group_id>")
def group(group_id):
    g_members = groups.get_normal_members(group_id)
    g_name = groups.get_name(group_id)
    g_overview = groups.group_overview(group_id)
    g_owner = groups.get_owner(group_id)
    g_admins = groups.get_admins(group_id)
    g_act_overview = activities.groups_activities_overview(group_id)
    g_formatted = activities.format_group_activities_for_overview(g_act_overview)
    g_admin_right = (session["user_id"], session["username"]) in g_admins
    return render_template("group_overview.html",
                            group_members=g_members,
                            group_name=g_name,
                            group_overview=g_overview,
                            group_owner=g_owner,
                            group_admins=g_admins,
                            admin_rights=g_admin_right,
                            group_id=group_id,
                            group_acts=g_formatted)


@app.route("/group/<int:group_id>/manage")
def manage_group(group_id):
    g_members = groups.get_normal_members(group_id)
    g_name = groups.get_name(group_id)
    g_admins = groups.get_admins(group_id)
    g_owner = groups.get_owner(group_id)
    return render_template("group_manager.html",
                            group_name=g_name,
                            group_members=g_members,
                            group_owner=g_owner,
                            group_admins=g_admins,
                            group_id=group_id)


@app.route("/group/<int:group_id>/all_activities")
def all_group_activities(group_id):
    g_name = groups.get_name(group_id)
    activity_list = activities.all_groups_activities_overview(group_id)
    formatted = activities.format_group_activities_for_overview(activity_list)
    return render_template("all_group_activities.html",
                           activity_list=formatted,
                           group_name=g_name
                           )


@app.route("/activity/<int:activity_id>/activity_comments", methods=["GET", "POST"])
def activity_comments(activity_id):
    a_info = activities.activity_info_short(activity_id)
    if request.method == "GET":
        return render_template("activity_comments.html",
                               comment_list=comments.get_comments(activity_id),
                               activity_id=activity_id,
                               activity_info=a_info)
    tools.verify_csrf(session["csrf_token"])
    if request.form["action"] == "delete":
        success, error_msg = comments.delete_comment(request.form)
        if success:
            return render_template("activity_comments.html",
                                    comment_list=comments.get_comments(activity_id),
                                    activity_id=activity_id,
                                    activity_info=a_info)
        return render_template("activity_comments.html",
                                comment_list=comments.get_comments(activity_id),
                                activity_id=activity_id,
                                error_message=error_msg)
    success, error_msg = comments.add_comment(request.form)
    if success:
        return render_template("activity_comments.html",
                                comment_list=comments.get_comments(activity_id),
                                activity_id=activity_id,
                                activity_info=a_info)
    return render_template("activity_comments.html",
                            comment_list=comments.get_comments(activity_id),
                            activity_id=activity_id,
                            error_message=error_msg)


@app.route("/user/<int:user_id>", methods=["GET", "POST"])
def user_overview(user_id):
    if request.method == "GET":
        u_overview = activities.user_activities_overview(user_id)
        u_formatted = activities.format_activities_for_overview(u_overview)
        u_username = users.get_username(user_id)
        if users.verify_view_right(user_id):
            u_overview = users.user_overview(user_id)
            u_public = users.is_public(user_id)
            return render_template("user_overview.html",
                                   user_id=user_id,
                                   user_public=u_public,
                                   username=u_username,
                                   user_overview=u_overview,
                                   user_list=u_formatted)
        return render_template("user_private.html",
                                username=u_username)
    tools.verify_csrf(session["csrf_token"])
    if request.form["make_profile"] == "public":
        users.make_public()
        return redirect("/user/"+str(user_id))
    users.make_private()
    return redirect("/user/"+str(user_id))


@app.route("/user/<int:user_id>/new_comments")
def new_comments(user_id):
    if session["user_id"] == user_id:
        c_list = comments.get_unseen_comments()
        if c_list:
            if comments.mark_as_read():
                session["unseen_comments"] = users.get_unseen_count()
        return render_template("new_comments.html",
                               comment_list=c_list)
    return redirect("/")


@app.route("/user/<int:user_id>/all_activities")
def all_activities(user_id):
    activity_list = activities.all_user_activities(user_id)
    formatted = activities.format_activities_for_overview(activity_list)
    if users.verify_view_right(user_id):
        return render_template("all_activities.html",
                            activity_list=formatted
                            )
    return render_template("user_private.html")


@app.route("/user/<int:user_id>/member_group_activities")
def all_user_group_activities(user_id):
    if not users.verify_user(user_id):
        return render_template("no_rights.html")
    activity_list = activities.all_user_group_activities()
    formatted = activities.format_group_activities_for_overview(activity_list)
    return render_template("all_user_group_activities.html",
                           activity_list=formatted
                           )


@app.route("/leaderboard/<int:category>/<int:stat>")
def leaderboard(category, stat):
    if category == 1:
        if stat == 1:
            return render_template("leaderboard_users.html",
                                user_list=users.user_leaderboard_total_dist(),
                                ordered=["▼"," "," "," "," "])
        if stat == 2:
            return render_template("leaderboard_users.html",
                                user_list=users.user_leaderboard_total_walked(),
                                ordered=[" ","▼"," "," "," "])
        if stat == 3:
            return render_template("leaderboard_users.html",
                                user_list=users.user_leaderboard_total_ran(),
                                ordered=[" "," ","▼"," "," "])
        if stat == 4:
            return render_template("leaderboard_users.html",
                                user_list=users.user_leaderboard_total_cycled(),
                                ordered=[" "," "," ","▼"," "])
        if stat == 5:
            return render_template("leaderboard_users.html",
                                user_list=users.user_leaderboard_total_time(),
                                ordered=[" "," "," "," ","▼"])
    if stat == 1:
        return render_template("leaderboard_groups.html",
                            group_list=groups.group_leaderboard_total_dist(),
                            ordered=["▼"," "," "," "," "])
    if stat == 2:
        return render_template("leaderboard_groups.html",
                            group_list=groups.group_leaderboard_total_walked(),
                            ordered=[" ","▼"," "," "," "])
    if stat == 3:
        return render_template("leaderboard_groups.html",
                            group_list=groups.group_leaderboard_total_ran(),
                            ordered=[" "," ","▼"," "," "])
    if stat == 4:
        return render_template("leaderboard_groups.html",
                            group_list=groups.group_leaderboard_total_cycled(),
                            ordered=[" "," "," ","▼"," "])
    if stat == 5:
        return render_template("leaderboard_groups.html",
                            group_list=groups.group_leaderboard_total_time(),
                            ordered=[" "," "," "," ","▼"])
