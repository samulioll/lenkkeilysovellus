from flask import session, abort


def return_valid_time(time):
    parts = time.split(":")
    for part in parts:
        if len(part) > 2 or int(part) > 59:
            return False
    return int(parts[2]) + (60 * int(parts[1])) + (3600 * int(parts[0]))


def format_time(time):
    if not time:
        return "00:00:00"
    hours = str(time // 3600)
    mins = str((time % 3600) // 60)
    secs = str((time % 3600) % 60)
    if len(hours) == 1:
        hours = "0"+hours
    if len(mins) == 1:
        mins = "0"+mins
    if len(secs) == 1:
        secs = "0"+secs
    return str(hours) + ":" + str(mins) + ":" + str(secs)


def format_date(date):
    parts = date.split("_")
    formatted = parts[0] + " " + parts[1]
    return formatted


def verify_csrf(token):
    if token != session["csrf_token"]:
        abort(403)

def format_leaderboard(ranked_list):
    return_list = []
    for entry in ranked_list:
        name = entry[0]
        name_id = entry[1]
        dist = entry[2]
        walk = entry [3]
        run = entry[4]
        cycle = entry[5]
        time = format_time(entry[6])
        return_list.append([name, name_id, dist, walk, run, cycle, time])
    return return_list

def sorted_by_icon(stat):
    icon_list = []
    for i in range(1, 6):
        if i == stat:
            icon_list.append("▼")
        icon_list.append(" ")
    return icon_list