# Examples:
# {countdown@0:00}
# {countdown@12:00PM PST}
# {countdown@21:00 PST}
# {countdown@Sunday 0:00}
# {countdown@Monday 0:00,Wednesday 0:00,Friday 0:00}
# {countdown@1/20/2015 0:00}
# {countdown@1/1 0:00}
# {countdown@1/20/2015 0:00,1/21/2015 0:00,1/22/2015 0:00}
# {countdown@15:00,Friday 6:00PM,1/1 7:00 PST,12/22/2015 9:00 PM}

from bot.data import timezones
from bot.data.timedelta import format as timedeltaFormat
import datetime
import re

_pattern = r"(?:(?:(0?[1-9]|1[012])[\-/](0?[1-9]|[12][0-9]|3[01])"
_pattern += r"(?:[\-/](\d{1,4}))?|(Sunday|Monday|Tuesday|Wednesday|Thursday|"
_pattern += r"Friday|Saturday|Sun|Mon|Tue|Wed|Thu|Fri|Sat)) )?"
_pattern += r"(?:(?:(0?[1-9]|1[0-2]):([0-5][0-9])"
_pattern += r"(?::([0-5][0-9])(?:\.(\d{1,6}))?)?([AP]M?)|"
_pattern += r"([01]?[0-9]|2[0-3]):([0-5][0-9])"
_pattern += r"(?::([0-5][0-9])(?:\.(\d{1,6}))?)?))(?: (.*))?"

_cooldownPattern = r"(\d{1,2}(?:\.\d{1,})?|100)%|"
_cooldownPattern += r"(?!$)(?:(\d{1,})w)?(?:(\d{1,})d)?"
_cooldownPattern += r"(?:([01]?[0-9]|2[0-3])h)?(?:([0-5]?[0-9])m)?"
_cooldownPattern += r"(?:([0-5]?[0-9])s)?(?<!^)"

_12HourFormat = '%m/%d/%Y %I:%M%p %Z'
_24HourFormat = '%m/%d/%Y %I:%M%p %Z'

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

daysOfWeek = {
    'sunday': SUNDAY,
    'monday': MONDAY,
    'tuesday': TUESDAY,
    'wednesday': WEDNESDAY,
    'thursday': THURSDAY,
    'friday': FRIDAY,
    'saturday': SATURDAY,
    
    'sun': SUNDAY,
    'mon': MONDAY,
    'tue': TUESDAY,
    'wed': WEDNESDAY,
    'thu': THURSDAY,
    'fri': FRIDAY,
    'sat': SATURDAY,
    }

def fieldCountdown(args):
    if args.field.lower() == 'countdown':
        cooldown = None
        dateInstances = []
        for i, args.param in enumerate(params.split(',')):
            if i == 0:
                cooldown = _getCooldown(args.param)
                if cooldown is not None:
                    continue
            pds = _parseDateString(args.param.strip())
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDateTimes = [_getNextDateTime(args.timestamp, *i)
                         for i in dateInstances]
        pastDateTimes = [_getPastDateTime(args.timestamp, *i)
                         for i in dateInstances]
        nextDateTimes = [dt for dt in nextDateTimes if dt is not None]
        pastDateTimes = [dt for dt in pastDateTimes if dt is not None]
        if len(nextDateTimes) == 0:
            return args.default if args.default else 'has passed'
        else:
            next = min(dt[0] for dt in nextDateTimes)
            timestamp = args.timestamp.replace(tzinfo=timezones.utc)
            if len(pastDateTimes) > 0 and cooldown:
                past = max(dt[0] for dt in pastDateTimes)
                if _testCooldown(cooldown, past, next, timestamp) < 0:
                    return args.default if args.default else 'has passed'
            delta = timedeltaFormat(next - timestamp)
            return args.prefix + delta + args.suffix
    return None

def fieldSince(args):
    if args.field.lower() == 'since':
        cooldown = 0
        dateInstances = []
        for i, args.param in enumerate(params.split(',')):
            if i == 0:
                cooldown = _getCooldown(args.param)
                if cooldown is not None:
                    continue
            pds = _parseDateString(args.param.strip())
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDateTimes = [_getNextDateTime(args.timestamp, *i)
                         for i in dateInstances]
        pastDateTimes = [_getPastDateTime(args.timestamp, *i)
                         for i in dateInstances]
        nextDateTimes = [dt for dt in nextDateTimes if dt is not None]
        pastDateTimes = [dt for dt in pastDateTimes if dt is not None]
        if len(pastDateTimes) == 0:
            return args.default if args.default else 'is coming'
        else:
            past = max(dt[0] for dt in pastDateTimes)
            timestamp = args.timestamp.replace(tzinfo=timezones.utc)
            if len(nextDateTimes) > 0 and cooldown:
                next = min(dt[0] for dt in nextDateTimes)
                if _testCooldown(cooldown, past, next, timestamp) >= 0:
                    return args.default if args.default else 'is coming'
            delta = timedeltaFormat(timestamp - past)
            return args.prefix + delta + args.suffix
    return None

def fieldNext(args):
    if args.field.lower() in ['next', 'future']:
        dateInstances = []
        for i, args.param in enumerate(params.split(',')):
            if i == 0:
                match = re.match(_cooldownPattern, args.param.strip())
                if match is not None:
                    continue
            pds = _parseDateString(args.param.strip())
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDateTimes = [_getNextDateTime(args.timestamp, *i)
                         for i in dateInstances]
        nextDateTimes = [dt for dt in nextDateTimes if dt is not None]
        if len(nextDateTimes) == 0:
            return args.default if args.default else 'None'
        else:
            nextDateTime = min(nextDateTimes, key=lambda dt: dt[0])
            format = _24HourFormat if nextDateTime[1] else _12HourFormat
            return args.prefix + nextDateTime[0].strftime(format) + args.suffix
    return None

def fieldPrevious(args):
    if args.field.lower() in ['prev', 'previous', 'past']:
        dateInstances = []
        for i, args.param in enumerate(params.split(',')):
            if i == 0:
                match = re.match(_cooldownPattern, args.param.strip())
                if match is not None:
                    continue
            pds = _parseDateString(args.param.strip())
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        pastDateTimes = [_getPastDateTime(args.timestamp, *i)
                         for i in dateInstances]
        pastDateTimes = [dt for dt in pastDateTimes if dt is not None]
        if len(pastDateTimes) == 0:
            return args.default if args.default else 'has passed'
        else:
            pastDateTime = max(pastDateTimes, key=lambda dt: dt[0])
            format = _24HourFormat if pastDateTime[1] else _12HourFormat
            return args.prefix + pastDateTime[0].strftime(format) + args.suffix
    return None

def _parseDateString(string):
    match = re.fullmatch(_pattern, string, re.IGNORECASE)
    if match is None:
        return None
    g = match.groups()
    seconds = 0
    microseconds = 0
    if g[9] is not None and g[10] is not None:
        hour = int(g[9])
        minute = int(g[10])
        if g[11] is not None:
            seconds = int(g[11])
            if g[12] is not None:
                microseconds = int(g[12])
        is24Hour = True
    elif g[4] is not None and g[5] is not None and g[8] is not None:
        hour = int(g[4])
        minute = int(g[5])
        if g[6] is not None:
            seconds = int(g[6])
            if g[7] is not None:
                microseconds = int(g[7])
        if g[8][0].lower() == 'p':
            hour += 12
        is24Hour = False
    else:
        return None
    if g[13] is not None and g[13].lower() in timezones.abbreviations:
        timezone = timezones.abbreviations[g[13].lower()]
    else:
        timezone = timezones.utc
    timeOfDay = datetime.time(hour, minute, seconds, microseconds, timezone)
    dayofweek = None
    date = None
    if g[3] is not None:
        dayofweek = daysOfWeek[g[3].lower()]
    elif g[0] is not None and g[1] is not None:
        month = int(g[0])
        day = int(g[1])
        if g[2] is not None:
            year = int(g[2])
        else:
            year = None
        date = (year, month, day)

    return (timeOfDay, dayofweek, date, is24Hour)

def _getNextDateTime(now, timeOfDay, dayofweek, date, is24Hour):
    now = now.replace(tzinfo=timezones.utc)
    today = datetime.date.today()
    if date is not None:
        if date[0] is not None:
            dt = datetime.datetime.combine(datetime.date(*date), timeOfDay)
            if dt > now:
                return dt, is24Hour
            else:
                return None
        ldate = list(date)
        ldate[0] = today.year
        # For February 29
        while(True):
            try:
                actualDate = datetime.date(*ldate)
                break
            except ValueError:
                ldate[0] += 1
        dt = datetime.datetime.combine(actualDate, timeOfDay)
        if dt > now:
            return dt, is24Hour
        else:
            year = actualDate.year + 1
            # For February 29
            while(True):
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year += 1
            return datetime.datetime.combine(actualDate, timeOfDay), is24Hour
    elif dayofweek is not None:
        daysToAdd = dayofweek - today.weekday()
        if daysToAdd < 0:
            daysToAdd += 7
        actualDate = today + datetime.timedelta(days=daysToAdd)
        dt = datetime.datetime.combine(actualDate, timeOfDay)
        if dt > now:
            return dt, is24Hour
        else:
            return dt + datetime.timedelta(days=7), is24Hour
    else:
        dt = datetime.datetime.combine(today, timeOfDay)
        if dt > now:
            return dt, is24Hour
        else:
            return dt + datetime.timedelta(days=1), is24Hour

def _getPastDateTime(now, timeOfDay, dayofweek, date, is24Hour):
    now = now.replace(tzinfo=timezones.utc)
    today = datetime.date.today()
    if date is not None:
        if date[0] is not None:
            dt = datetime.datetime.combine(datetime.date(*date), timeOfDay)
            if dt <= now:
                return dt, is24Hour
            else:
                return None
        ldate = list(date)
        ldate[0] = today.year
        # For February 29
        while(True):
            try:
                actualDate = datetime.date(*ldate)
                break
            except ValueError:
                ldate[0] -= 1
        dt = datetime.datetime.combine(actualDate, timeOfDay)
        if dt <= now:
            return dt, is24Hour
        else:
            year = actualDate.year + 1
            # For February 29
            while(True):
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year -= 1
            return datetime.datetime.combine(actualDate, timeOfDay), is24Hour
    elif dayofweek is not None:
        daysToAdd = dayofweek - today.weekday()
        if daysToAdd > 0:
            daysToAdd -= 7
        actualDate = today + datetime.timedelta(days=daysToAdd)
        dt = datetime.datetime.combine(actualDate, timeOfDay)
        if dt <= now:
            return dt, is24Hour
        else:
            return dt - datetime.timedelta(days=7), is24Hour
    else:
        dt = datetime.datetime.combine(today, timeOfDay)
        if dt <= now:
            return dt, is24Hour
        else:
            return dt - datetime.timedelta(days=1), is24Hour

def _getCooldown(string):
    match = re.match(_cooldownPattern, string.strip())
    if match is not None:
        groups = match.groups()
        if groups[0] is not None:
            return float(groups[0]) / 100.0
        elif (groups[1] is not None or
              groups[2] is not None or
              groups[3] is not None or
              groups[4] is not None or
              groups[5] is not None):
            weeks = int(groups[1] or 0)
            days = int(groups[2] or 0)
            hours = int(groups[3] or 0)
            minutes = int(groups[4] or 0)
            seconds = int(groups[5] or 0)
            return datetime.timedelta(weeks=weeks, days=days, hours=hours,
                                      minutes=minutes, seconds=seconds)
    return None

def _testCooldown(cooldown, past, future, now):
    if cooldown is None:
        return 0
    if isinstance(cooldown, float):
        total = (future - past).total_seconds()
        timespan = (now - past).total_seconds()
        if (timespan / total) > cooldown:
            return 1
        else:
            return -1
    if isinstance(cooldown, datetime.timedelta):
        timespan = now - past
        if timespan > cooldown:
            return 1
        else:
            return -1
    return 0
