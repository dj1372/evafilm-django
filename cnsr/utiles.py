def string_to_time(str_time):
    """
    @parameter a str with 8 char => time in second
    """
    str_time = str_time.split(":")
    hour = int(str_time[0]) * 3600
    minute = int(str_time[1]) * 60
    second = int(str_time[2])
    return str(hour + minute + second)


def time_to_string(time_str):
    """
    @parameter time in second  => a str with 8 char
    """
    hour = int(time_str) // 3600
    cary = int(time_str) % 3600
    minute = int(cary) // 60
    second = int(cary) % 60
    if hour < 10 and minute < 10 and second < 10:
        return f"0{hour}:0{minute}:0{second}"
    elif hour > 10 and minute < 10 and second < 10:
        return f"{hour}:0{minute}:0{second}"
    elif hour > 10 and minute > 10 and second < 10:
        return f"{hour}:{minute}:0{second}"
    elif hour > 10 and minute > 10 and second > 10:
        return f"{hour}:{minute}:{second}"
    elif hour < 10 and minute > 10 and second < 10:
        return f"0{hour}:{minute}:0{second}"
    elif hour < 10 and minute < 10 and second > 10:
        return f"0{hour}:0{minute}:{second}"
