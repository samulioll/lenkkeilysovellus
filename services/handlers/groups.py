from flask import session
from sqlalchemy import text
from db import db
from services import tools


def join_group(group_id):
    sql = text("""INSERT INTO groupmembers
                    (user_id, group_id, owner_status, admin_status, visible) 
                    VALUES (:user_id, :group_id, FALSE, FALSE, TRUE)""")
    db.session.execute(sql, {"user_id": int(session["user_id"]),
                             "group_id": group_id})
    db.session.commit()
    return True


def join_group_owner(group_id):
    sql = text("""INSERT INTO groupmembers
                    (user_id, group_id, owner_status, admin_status, visible) 
                    VALUES (:user_id, :group_id, TRUE, TRUE, TRUE)""")
    db.session.execute(sql, {"user_id": int(session["user_id"]),
                             "group_id": group_id})
    db.session.commit()
    return True


def leave_group(group_id, user_id):
    sql = text("""UPDATE groupmembers
                    SET visible=FALSE 
                    WHERE user_id=:user_id AND group_id=:group_id""")
    db.session.execute(sql, {"user_id": user_id,
                                "group_id": group_id})
    db.session.commit()
    return True


def create_group(form):
    sql = text("SELECT id FROM groups WHERE name=:group_name")
    result = db.session.execute(sql, {"group_name": form["group_name"]})
    name_taken = result.fetchone()
    if name_taken:
        return False, "Group name already in use", None
    sql = text("""INSERT INTO groups
                  (name, visible) 
                  VALUES 
                  (:group_name, TRUE)
                  RETURNING id""")
    group_id = db.session.execute(
        sql, {"group_name": form["group_name"]}).fetchone()[0]
    db.session.commit()
    return True, None, group_id


def delete_group(group_id):
    sql = text("""UPDATE groups
                  SET visible=FALSE
                  WHERE id=:group_id""")
    db.session.execute(sql, {"group_id": group_id})
    db.session.commit()


def user_groups_overview():
    sql = text("""SELECT G.name, G.id
                  FROM groups G, groupmembers M
                  WHERE G.id=M.group_id AND M.user_id=:user_id AND M.visible=TRUE
                  AND G.visible=TRUE""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return result.fetchall()


def get_groups():
    result = db.session.execute(
        text("SELECT * FROM groups WHERE visible=TRUE"))
    return result.fetchall()


def get_user_groups():
    sql = text("""SELECT G.id, G.name, G.visible
                  FROM groups G, groupmembers M
                  WHERE G.id=M.group_id AND M.user_id=:user_id
                  AND M.visible=TRUE""")
    result = db.session.execute(sql, {"user_id": session["user_id"]})
    return result.fetchall()


def group_overview(group_id):
    total_dist = get_total_distance(group_id)
    walked = get_distance_walked(group_id)
    ran = get_distance_ran(group_id)
    cycled = get_distance_cycled(group_id)
    total_time = tools.format_time(get_total_time(group_id))
    return (total_dist, walked, ran, cycled, total_time)


def get_name(group_id):
    sql = text("SELECT name FROM groups WHERE id=:group_id")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_total_distance(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R
                  ON A.route_id=R.id
                  WHERE A.user_id IN
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_distance_walked(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R
                  ON A.route_id=R.id
                  WHERE A.user_id IN
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=1""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_distance_ran(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R
                  ON A.route_id=R.id
                  WHERE A.user_id IN
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=2""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_distance_cycled(group_id):
    sql = text("""SELECT SUM(R.length)
                  FROM activities A LEFT JOIN routes R
                  ON A.route_id=R.id
                  WHERE A.user_id IN
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)
                  AND A.sport_id=3""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_total_time(group_id):
    sql = text("""SELECT SUM(duration)
                  FROM activities
                  WHERE user_id IN 
                  (SELECT user_id FROM groupmembers WHERE group_id=:group_id)""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()[0]


def get_all_members(group_id):
    sql = text("""SELECT U.id, U.username
                  FROM users U, groupmembers G
                  WHERE U.id=G.user_id and G.group_id=:group_id AND G.visible=TRUE""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchall()


def get_normal_members(group_id):
    sql = text("""SELECT U.id, U.username
                  FROM users U, groupmembers G
                  WHERE U.id=G.user_id and G.group_id=:group_id AND G.visible=TRUE
                  AND owner_status=FALSE AND admin_status=FALSE""")
    result = db.session.execute(sql, {"group_id": group_id})
    if result:
        return result.fetchall()
    return None


def get_owner(group_id):
    sql = text("""SELECT U.id, U.username
                  FROM users U, groupmembers G
                  WHERE U.id=G.user_id AND G.group_id=:group_id 
                  AND G.owner_status=TRUE AND G.visible=TRUE""")
    result = db.session.execute(sql, {"group_id": group_id})
    return result.fetchone()


def get_admins(group_id):
    sql = text("""SELECT U.id, U.username
                  FROM users U, groupmembers G
                  WHERE U.id=G.user_id AND G.group_id=:group_id 
                  AND G.admin_status=TRUE AND G.visible=TRUE""")
    result = db.session.execute(sql, {"group_id": group_id})
    if result:
        return result.fetchall()
    return None


def get_other_admins(group_id):
    sql = text("""SELECT U.id, U.username
                  FROM users U, groupmembers G
                  WHERE U.id=G.user_id AND G.group_id=:group_id 
                  AND G.admin_status=TRUE AND G.visible=TRUE AND G.user_id!=:user_id""")
    result = db.session.execute(sql, {"group_id": group_id,
                                      "user_id": session["user_id"]})
    return result.fetchall()


def make_admin(group_id, user_id):
    sql = text("""UPDATE groupmembers
                  SET admin_status=TRUE
                  WHERE user_id=:user_id AND group_id=:group_id""")
    db.session.execute(sql, {"group_id": group_id,
                                      "user_id": user_id})
    db.session.commit()
    return True


def demote_admin(group_id, user_id):
    sql = text("""UPDATE groupmembers
                  SET admin_status=FALSE
                  WHERE user_id=:user_id AND group_id=:group_id""")
    db.session.execute(sql, {"group_id": group_id,
                                      "user_id": user_id})
    db.session.commit()
    return True


def get_next_owner(group_id):
    try:
        first_admin = get_other_admins(group_id)[0]
    except:
        first_admin = None
    if not first_admin:
        try:
            first_member = get_normal_members(group_id)[0]
        except:
            first_member = None
        if not first_member:
            return False
        return first_member
    return first_admin


def make_owner(group_id, user_id):
    sql = text("""UPDATE groupmembers
                  SET owner_status=TRUE, admin_status=TRUE
                  WHERE user_id=:user_id AND group_id=:group_id""")
    db.session.execute(sql, {"group_id": group_id,
                             "user_id": user_id[0]})
    db.session.commit()
    return True


def group_leaderboard_total_dist():
    quer = text("""SELECT name AS group, id AS group_id, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran) AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, G.id, T.Total, T.Walked, T.Ran, T.Cycled, T.time
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
                   GROUP BY name, id
                   ORDER BY total DESC""")
    result = db.session.execute(quer)
    if result:
        return tools.format_leaderboard(result)
    return None


def group_leaderboard_total_walked():
    quer = text("""SELECT name AS group, id AS group_id, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran) AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, G.id, T.Total, T.Walked, T.Ran, T.Cycled, T.time
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
                   GROUP BY name, id
                   ORDER BY walked DESC""")
    result = db.session.execute(quer)
    if result:
        return tools.format_leaderboard(result)
    return None


def group_leaderboard_total_ran():
    quer = text("""SELECT name AS group, id AS group_id, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran) AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, G.id, T.Total, T.Walked, T.Ran, T.Cycled, T.time
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
                   GROUP BY name, id
                   ORDER BY ran DESC""")
    result = db.session.execute(quer)
    if result:
        return tools.format_leaderboard(result)
    return None


def group_leaderboard_total_cycled():
    quer = text("""SELECT name AS group, id AS group_id, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran) AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, G.id, T.Total, T.Walked, T.Ran, T.Cycled, T.time
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
                   GROUP BY name, id
                   ORDER BY cycled DESC""")
    result = db.session.execute(quer)
    if result:
        return tools.format_leaderboard(result)
    return None


def group_leaderboard_total_time():
    quer = text("""SELECT name AS group, id AS group_id, SUM(total) AS total, SUM(walked) AS walked, 
                   SUM(ran) AS ran, SUM(cycled) AS cycled, SUM(time) AS time
                   FROM
                   (SELECT U.username AS Username, G.name, G.id, T.Total, T.Walked, T.Ran, T.Cycled, T.time
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
                   GROUP BY name, id
                   ORDER BY time DESC""")
    result = db.session.execute(quer)
    if result:
        return tools.format_leaderboard(result)
    return None
