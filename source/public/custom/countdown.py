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

from datetime import date, datetime, time, timedelta
from typing import List, Match, NamedTuple, Optional, Sequence, Tuple, Union
from ...data import CustomFieldArgs
from ...data.timedelta import format as timedeltaFormat
from ...data import timezones
import re

Date = NamedTuple('Date', [('year', Optional[int]),
                           ('month', int),
                           ('day', int)])
DateTime = NamedTuple('DateTime', [('timestamp', datetime),
                                   ('format24', bool)])
DateTimeInstance = NamedTuple('DateTimeInstance',
                              [('timeofday', time),
                               ('dayofweek', Optional[int]),
                               ('date', Optional[Date]),
                               ('format24', bool)])

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


def fieldCountdown(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'countdown':
        cooldown = None  # type: Optional[Union[float, timedelta]]
        dateInstances = []  # type: List[DateTimeInstance]
        for i, param in enumerate(args.param.split(',')):  # --type: int, str
            if i == 0:
                cooldown = getCooldown(param)
                if cooldown is not None:
                    continue
            pds = _parseDateString(param.strip())  # type: Optional[DateTimeInstance]
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDts = [getNextDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        pastDts = [getPastDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        nextDateTimes = [dt for dt in nextDts if dt is not None]  # type: List[DateTime]
        pastDateTimes = [dt for dt in pastDts if dt is not None]  # type: List[DateTime]
        if len(nextDateTimes) == 0:
            return args.default if args.default else 'has passed'
        else:
            next = min(dt.timestamp for dt in nextDateTimes)  # type: datetime
            timestamp = args.timestamp.replace(tzinfo=timezones.utc)  # type: datetime
            if len(pastDateTimes) > 0 and cooldown:
                past = max(dt.timestamp for dt in pastDateTimes)  # type: datetime
                if testCooldown(cooldown, past, next, timestamp) < 0:
                    return args.default if args.default else 'has passed'
            delta = timedeltaFormat(next - timestamp)  # type: str
            return args.prefix + delta + args.suffix
    return None


def fieldSince(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'since':
        cooldown = 0  # type: Optional[Union[float, timedelta]]
        dateInstances = []  # type: List[DateTimeInstance]
        for i, param in enumerate(args.param.split(',')):  # --type: int, str
            if i == 0:
                cooldown = getCooldown(param)
                if cooldown is not None:
                    continue
            pds = _parseDateString(param.strip())  # type: Optional[DateTimeInstance]
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDts = [getNextDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        pastDts = [getPastDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        nextDateTimes = [dt for dt in nextDts if dt is not None]  # type: List[DateTime]
        pastDateTimes = [dt for dt in pastDts if dt is not None]  # type: List[DateTime]
        if len(pastDateTimes) == 0:
            return args.default if args.default else 'is coming'
        else:
            past = max(dt.timestamp for dt in pastDateTimes)  # type: datetime
            timestamp = args.timestamp.replace(tzinfo=timezones.utc)  # type: datetime
            if len(nextDateTimes) > 0 and cooldown:
                next = min(dt.timestamp for dt in nextDateTimes)  # type: datetime
                if testCooldown(cooldown, past, next, timestamp) >= 0:
                    return args.default if args.default else 'is coming'
            delta = timedeltaFormat(timestamp - past)  # type: str
            return args.prefix + delta + args.suffix
    return None


def fieldNext(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() in ['next', 'future']:
        dateInstances = []  # type: List[DateTimeInstance]
        for i, param in enumerate(args.param.split(',')):
            if i == 0:
                if re.match(_cooldownPattern, param.strip()) is not None:
                    continue
            pds = _parseDateString(param.strip())  # type: Optional[DateTimeInstance]
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        nextDts = [getNextDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        nextDateTimes = [dt for dt in nextDts if dt is not None]  # type: List[DateTime]
        if len(nextDateTimes) == 0:
            return args.default if args.default else 'None'
        else:
            nextDateTime = min(nextDateTimes, key=lambda dt: dt.timestamp)  # type: DateTime
            format = _24HourFormat if nextDateTime.format24 else _12HourFormat
            return (args.prefix + nextDateTime.timestamp.strftime(format)
                    + args.suffix)
    return None


def fieldPrevious(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() in ['prev', 'previous', 'past']:
        dateInstances = []  # type: List[DateTimeInstance]
        for i, param in enumerate(args.param.split(',')):
            if i == 0:
                if re.match(_cooldownPattern, param.strip()) is not None:
                    continue
            pds = _parseDateString(param.strip())  # type: Optional[DateTimeInstance]
            if pds is not None:
                dateInstances.append(pds)
        if dateInstances is None:
            return None
        pastDts = [getPastDateTime(args.timestamp, *i)
                   for i in dateInstances]  # type: List[Optional[DateTime]]
        pastDateTimes = [dt for dt in pastDts if dt is not None]  # type: List[DateTime]
        if len(pastDateTimes) == 0:
            return args.default if args.default else 'has passed'
        else:
            pastDateTime = max(pastDateTimes, key=lambda dt: dt.timestamp)  # type: DateTime
            format = _24HourFormat if pastDateTime.format24 else _12HourFormat
            return (args.prefix + pastDateTime.timestamp.strftime(format)
                    + args.suffix)
    return None


def _parseDateString(string: str) -> Optional[DateTimeInstance]:
    match = re.fullmatch(_pattern, string, re.IGNORECASE)  # type: Match[str]
    if match is None:
        return None
    g = match.groups()  # type: Sequence[str]
    seconds = 0  # type: int
    microseconds = 0  # type: int
    if g[9] is not None and g[10] is not None:
        hour = int(g[9])  # type: int
        minute = int(g[10])  # type: int
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
    timeOfDay = time(hour, minute, seconds, microseconds, timezone)  # type: time
    dayofweek = None  # type: Optional[int]
    date = None  # type: Optional[Date]
    if g[3] is not None:
        dayofweek = daysOfWeek[g[3].lower()]
    elif g[0] is not None and g[1] is not None:
        month = int(g[0])
        day = int(g[1])
        if g[2] is not None:
            year = int(g[2])
        else:
            year = None
        date = Date(year, month, day)

    return DateTimeInstance(timeOfDay, dayofweek, date, is24Hour)


def getNextDateTime(now: datetime,
                    timeOfDay: time,
                    dayofweek: Optional[int],
                    date_: Optional[Date],
                    is24Hour: bool) -> Optional[DateTime]:
    now = now.replace(tzinfo=timezones.utc)
    today = date.today()  # time: date
    if date_ is not None:
        if date_.year is not None:
            dt = datetime.combine(date(*date_), timeOfDay)  # type: datetime
            if dt > now:
                return DateTime(dt, is24Hour)
            else:
                return None
        ldate = [today.year, date_.month, date_.day]  # type: List[int]
        # For February 29
        while True:
            try:
                actualDate = date(*ldate)  # type: date
                break
            except ValueError:
                ldate[0] += 1
        dt = datetime.combine(actualDate, timeOfDay)
        if dt > now:
            return DateTime(dt, is24Hour)
        else:
            year = actualDate.year + 1  # type: int
            # For February 29
            while True:
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year += 1
            return DateTime(datetime.combine(actualDate, timeOfDay), is24Hour)
    elif dayofweek is not None:
        daysToAdd = dayofweek - today.weekday()  # type: int
        if daysToAdd < 0:
            daysToAdd += 7
        actualDate = today + timedelta(days=daysToAdd)
        dt = datetime.combine(actualDate, timeOfDay)
        if dt > now:
            return DateTime(dt, is24Hour)
        else:
            return DateTime(dt + timedelta(days=7), is24Hour)
    else:
        dt = datetime.combine(today, timeOfDay)
        if dt > now:
            return DateTime(dt, is24Hour)
        else:
            return DateTime(dt + timedelta(days=1), is24Hour)


def getPastDateTime(now: datetime,
                    timeOfDay: time,
                    dayofweek: Optional[int],
                    date_: Optional[Date],
                    is24Hour: bool) -> Optional[DateTime]:
    now = now.replace(tzinfo=timezones.utc)
    today = date.today()  # time: date
    if date_ is not None:
        if date_.year is not None:
            dt = datetime.combine(date(*date_), timeOfDay)  # type: datetime
            if dt <= now:
                return DateTime(dt, is24Hour)
            else:
                return None
        ldate = [today.year, date_.month, date_.day]  # type: List[int]
        # For February 29
        while True:
            try:
                actualDate = date(*ldate)  # type: date
                break
            except ValueError:
                ldate[0] -= 1
        dt = datetime.combine(actualDate, timeOfDay)
        if dt <= now:
            return DateTime(dt, is24Hour)
        else:
            year = actualDate.year + 1  # type: int
            # For February 29
            while True:
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year -= 1
            return DateTime(datetime.combine(actualDate, timeOfDay), is24Hour)
    elif dayofweek is not None:
        daysToAdd = dayofweek - today.weekday()  # type: int
        if daysToAdd > 0:
            daysToAdd -= 7
        actualDate = today + timedelta(days=daysToAdd)
        dt = datetime.combine(actualDate, timeOfDay)
        if dt <= now:
            return DateTime(dt, is24Hour)
        else:
            return DateTime(dt - timedelta(days=7), is24Hour)
    else:
        dt = datetime.combine(today, timeOfDay)
        if dt <= now:
            return DateTime(dt, is24Hour)
        else:
            return DateTime(dt - timedelta(days=1), is24Hour)


def getCooldown(string: str) -> Optional[Union[float, timedelta]]:
    match = re.match(_cooldownPattern, string.strip())  # type: Match[str]
    if match is not None:
        groups = match.groups()  # type: Sequence[str]
        if groups[0] is not None:
            return float(groups[0]) / 100.0
        elif (groups[1] is not None
              or groups[2] is not None
              or groups[3] is not None
              or groups[4] is not None
              or groups[5] is not None):
            weeks = int(groups[1] or 0)  # type: int
            days = int(groups[2] or 0)  # type: int
            hours = int(groups[3] or 0)  # type: int
            minutes = int(groups[4] or 0)  # type: int
            seconds = int(groups[5] or 0)  # type: int
            return timedelta(weeks=weeks, days=days, hours=hours,
                             minutes=minutes, seconds=seconds)
    return None


def testCooldown(cooldown: Optional[Union[float, timedelta]],
                 past: datetime,
                 future: datetime,
                 now: datetime) -> int:
    if cooldown is None:
        return 0
    if isinstance(cooldown, float):
        total = (future - past).total_seconds()  # type: float
        timespan = (now - past).total_seconds()  # type: float
        if (timespan / total) > cooldown:
            return 1
        else:
            return -1
    if isinstance(cooldown, timedelta):
        if now - past > cooldown:
            return 1
        else:
            return -1
    return 0
