def return_valid_time(time):
    parts = time.split(":")
    for part in parts:
        if len(part) > 2 or int(part) > 59:
            return False
    return int(parts[2]) + (60 * int(parts[1])) + (3600 * int(parts[0]))

def format_time(time):
    hours = time // 3600
    mins = (time % 3600) // 60
    secs = (time % 3600) % 60
    return str(hours) + ":" + str(mins) + ":" + str(secs)

def format_date(date):
    parts = date.split("_")
    formatted =  parts[0] + " " + parts[1]
    return formatted