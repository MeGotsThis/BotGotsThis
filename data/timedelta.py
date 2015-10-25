def format(timeDelta):
    formatted = []
    if timeDelta.days == 1:
        formatted.append('1 day')
    elif timeDelta.days > 1:
        formatted.append(str(timeDelta.days) + ' days')
    hours = timeDelta.seconds // 3600
    if hours == 1:
        formatted.append('1 hour')
    elif hours > 1:
        formatted.append(str(hours) + ' hours')
    minutes = timeDelta.seconds // 60 % 60
    if minutes == 1:
        formatted.append('1 minute')
    elif minutes > 1:
        formatted.append(str(minutes) + ' minutes')
    seconds = timeDelta.seconds % 60
    if seconds == 1:
        formatted.append('1 second')
    elif seconds > 1:
        formatted.append(str(seconds) + ' seconds')
    return ', '.join(formatted)
