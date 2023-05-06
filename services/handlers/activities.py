from datetime import datetime
from flask import session
from sqlalchemy import text
from services import tools
from db import db
from .users import get_username
from .activity_routes import get_activity_route


def add_activity(form):
    time = tools.return_valid_time(form["time"])
    if time:
        sql = text("""INSERT INTO activities
                        (user_id, sport_id, route_id, duration, date, visible) 
                        VALUES 
                        (:user_id, :sport_id, :route_id, :duration, :date, TRUE)""")
        db.session.execute(sql, {"user_id": int(session["user_id"]),
                                 "sport_id": int(form["sport"]),
                                 "route_id": int(form["routes"]),
                                 "duration": time,
                                 "date": str(datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
        db.session.commit()
        add_comment(form)
        return (True, "")
    return (False, "Invalid time")


def add_comment(form):
    if len(form["comment"]) < 1:
        return True
    sql = text("""INSERT INTO comments
                    (activity_id, user_id, content, date, visible)
                    VALUES 
                    (:activity_id, :user_id, :content, :date, TRUE)""")
    act_id_fetch = db.session.execute(
        text("SELECT COUNT(*) FROM activities"))
    activity_id = act_id_fetch.fetchone()[0]
    db.session.execute(sql, {"activity_id": int(activity_id),
                             "user_id": int(session["user_id"]),
                             "content": str(form["comment"]),
                             "date": str(datetime.utcnow().strftime("%Y-%m-%d_%H:%M"))})
    db.session.commit()
    return True


def user_activities_overview(user_id):
    sql = text("""SELECT id, user_id, sport_id, route_id, duration, date, visible
                  FROM activities 
                  WHERE user_id=:user_id AND visible=TRUE
                  ORDER BY id DESC 
                  LIMIT 5""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchall()


def user_groups_activities_overview():
    sql = text("""SELECT DISTINCT A.id, A.user_id, A.sport_id, A.route_id,
                  A.duration, A.date, A.visible
                  FROM activities A, groupmembers G 
                  WHERE A.visible=TRUE AND A.user_id=G.user_id AND G.user_id IN 
                  (SELECT DISTINCT U.id FROM users U, groupmembers G 
                  WHERE U.id=G.user_id AND G.group_id IN 
                  (SELECT DISTINCT group_id FROM groupmembers WHERE user_id=:user_id)) 
                  ORDER BY A.id DESC 
                  LIMIT 5""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return result.fetchall()


def all_user_activities(user_id):
    sql = text("""SELECT id, user_id, sport_id, route_id, duration, date, visible
                  FROM activities 
                  WHERE user_id=:user_id AND visible=TRUE
                  ORDER BY id DESC""")
    result = db.session.execute(sql, {"user_id": user_id})
    return result.fetchall()


def all_user_group_activities():
    sql = text("""SELECT DISTINCT A.id, A.user_id, A.sport_id, A.route_id,
                  A.duration, A.date, A.visible
                  FROM activities A, groupmembers G 
                  WHERE A.visible=TRUE AND A.user_id=G.user_id AND G.user_id IN 
                  (SELECT DISTINCT U.id FROM users U, groupmembers G 
                  WHERE U.id=G.user_id AND G.group_id IN 
                  (SELECT DISTINCT group_id FROM groupmembers WHERE user_id=:user_id)) 
                  ORDER BY A.id DESC""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return result.fetchall()


def format_activities_for_overview(act_list):
    activities = []
    for activity in act_list:
        sport = get_sport(activity.sport_id)
        activity_info = get_activity_route(activity.route_id)
        duration_str = tools.format_time(activity.duration)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        comment_count = get_comment_count(activity.id)
        activities.append([activity.id, sport, activity_info[0], activity_info[1],
                           duration_str, date_str, comment_count])
    return activities


def format_group_activities_for_overview(act_list):
    activities = []
    for activity in act_list:
        username = get_username(activity.user_id)
        sport = get_sport(activity.sport_id)
        activity_info = get_activity_route(activity.route_id)
        duration_str = tools.format_time(activity.duration)
        date_parts = activity.date.split("_")
        date_str = date_parts[0] + " " + date_parts[1]
        comment_count = get_comment_count(activity.id)
        activities.append([activity.id, username, sport, activity_info[0], activity_info[1],
                           duration_str, date_str, comment_count])
    return activities


def activity_info_short(activity_id):
    sql = text("""SELECT U.username, A.id, A.user_id, A.sport_id, A.route_id,
                  A.duration, A.date, A.visible
                  FROM users U,activities A
                  WHERE U.id=A.user_id AND A.id=:activity_id """)
    result = db.session.execute(sql, {"activity_id": activity_id})
    return format_activity_short(result.fetchone())


def format_activity_short(activity):
    username = activity.username
    sport = get_sport(activity.sport_id).capitalize()
    length = get_length(activity.route_id)
    parts = activity.date.split("_")
    date = parts[0]
    return username + " /// " + sport + " | " + str(length) + "km | " + date


def get_sport(sport_id):
    sport_sql = text("SELECT name FROM sports WHERE id=:sport_id")
    sport_fetch = db.session.execute(sport_sql, {"sport_id": sport_id})
    sport = sport_fetch.fetchone()[0]
    return sport


def get_length(route_id):
    length_sql = text("""SELECT length
                    FROM routes
                    WHERE id=:route_id""")
    length_fetch = db.session.execute(length_sql, {"route_id": route_id})
    length = length_fetch.fetchone()[0]
    return length


def user_leaderboard_total_dist():
    quer = text("""SELECT U.username AS Username, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE
                   ORDER BY T.Total DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None

def user_leaderboard_total_walked():
    quer = text("""SELECT U.username AS Username, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE
                   ORDER BY T.Walked DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def user_leaderboard_total_ran():
    quer = text("""SELECT U.username AS Username, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE
                   ORDER BY T.Ran DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def user_leaderboard_total_cycled():
    quer = text("""SELECT U.username AS Username, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE
                   ORDER BY T.Cycled DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None



def user_leaderboard_total_time():
    quer = text("""SELECT U.username AS Username, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE
                   ORDER BY T.Time DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def group_leaderboard_total_dist():
    quer = text("""SELECT name AS group, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran)AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U, groups G, groupmembers M,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE AND M.user_id=U.id AND G.id=M.group_id) AS X
                   GROUP BY name
                   ORDER BY total DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def group_leaderboard_total_walked():
    quer = text("""SELECT name AS group, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran)AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U, groups G, groupmembers M,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE AND M.user_id=U.id AND G.id=M.group_id) AS X
                   GROUP BY name
                   ORDER BY walked DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def group_leaderboard_total_ran():
    quer = text("""SELECT name AS group, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran)AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U, groups G, groupmembers M,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE AND M.user_id=U.id AND G.id=M.group_id) AS X
                   GROUP BY name
                   ORDER BY ran DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def group_leaderboard_total_cycled():
    quer = text("""SELECT name AS group, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran)AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U, groups G, groupmembers M,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE AND M.user_id=U.id AND G.id=M.group_id) AS X
                   GROUP BY name
                   ORDER BY cycled DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def group_leaderboard_total_time():
    quer = text("""SELECT name AS group, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran)AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, T.Total, T.Walked, T.Ran, T.Cycled, T.time
                   FROM
                   users U, groups G, groupmembers M,
                   (SELECT W.user_id AS User_id, COALESCE(Di.total,0) AS Total, COALESCE(W.walked,0) AS Walked,
                   COALESCE(W.ran,0) AS Ran, COALESCE(W.cycled,0) AS Cycled, COALESCE(W.time,0) AS Time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS total FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Di
                   FULL JOIN
                   (SELECT R.user_id, W.walked, R.ran, R.cycled, R.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS walked FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=1 AND A.route_id=R.id GROUP BY A.user_id) W
                   FULL JOIN
                   (SELECT C.user_id, R.ran, C.cycled, C.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS ran FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=2 AND A.route_id=R.id GROUP BY A.user_id) R
                   FULL JOIN
                   (SELECT Du.user_id, C.cycled, Du.time
                   FROM
                   (SELECT A.user_id, SUM(R.length) AS cycled FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.sport_id=3 AND A.route_id=R.id GROUP BY A.user_id) C
                   FULL JOIN
                   (SELECT A.user_id, SUM(A.duration) AS time FROM routes R, activities A 
                   WHERE A.visible=TRUE AND A.route_id=R.id GROUP BY A.user_id) Du
                   ON C.user_id=Du.user_id) C
                   ON R.user_id=C.user_id) R
                   ON W.user_id=R.user_id) W
                   ON Di.user_id=W.user_id) T
                   WHERE U.id=T.User_id AND U.public=TRUE AND M.user_id=U.id AND G.id=M.group_id) AS X
                   GROUP BY name
                   ORDER BY time DESC""")
    result = db.session.execute(quer)
    if result:
        return result
    return None


def get_comment_count(activity_id):
    sql = text("""SELECT COUNT(id)
                    FROM comments
                    WHERE activity_id=:activity_id AND visible=TRUE""")
    result = db.session.execute(sql, {"activity_id": activity_id})
    if result:
        return result.fetchone()[0]
    return False
