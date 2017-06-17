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
from typing import Dict, List, Match, NamedTuple, Optional, Sequence, Union
from ...data import CustomFieldArgs
from ...data.timedelta import format as format_timedelta
from ...data import timezones
import math
import re


class Date(NamedTuple):
    year: Optional[int]
    month: int
    day: int


class DateTime(NamedTuple):
    timestamp: datetime
    format24: bool


class DateTimeInstance(NamedTuple):
    timeofday: time
    dayofweek: Optional[int]
    date: Optional[Date]
    format24: bool


class NextPastCooldown(NamedTuple):
    next: Optional[DateTime]
    past: Optional[DateTime]
    cooldown: Optional[float]


_pattern: str = (
    r'(?:(?:(0?[1-9]|1[012])[\-/](0?[1-9]|[12][0-9]|3[01])'
    r'(?:[\-/](\d{1,4}))?|(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|'
    r'Saturday|Sun|Mon|Tue|Wed|Thu|Fri|Sat)) )?'
    r'(?:(?:(0?[1-9]|1[0-2]):([0-5][0-9])'
    r'(?::([0-5][0-9])(?:\.(\d{1,6}))?)?([AP]M?)|'
    r'([01]?[0-9]|2[0-3]):([0-5][0-9])'
    r'(?::([0-5][0-9])(?:\.(\d{1,6}))?)?))(?: (.*))?'
    )

_cooldownPattern: str = (
    r'(\d{1,2}(?:\.\d{1,})?|100)%|'
    r'(?!$)(?:(\d{1,})w)?(?:(\d{1,})d)?(?:([01]?[0-9]|2[0-3])h)?'
    r'(?:([0-5]?[0-9])m)?(?:([0-5]?[0-9])s)?(?<!^)'
    )

_12HourFormat: str = '%m/%d/%Y %I:%M%p %Z'
_24HourFormat: str = '%m/%d/%Y %H:%M %Z'

MONDAY: int = 0
TUESDAY: int = 1
WEDNESDAY: int = 2
THURSDAY: int = 3
FRIDAY: int = 4
SATURDAY: int = 5
SUNDAY: int = 6

daysOfWeek: Dict[str, int] = {
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


async def fieldCountdown(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'countdown' and args.param is not None:
        timestamp: datetime = args.timestamp.replace(tzinfo=timezones.utc)
        npc: NextPastCooldown = parse_next_past_cooldown(args.param, timestamp)
        next: Optional[DateTime]
        past: Optional[DateTime]
        cooldown: float
        next, past, cooldown = npc
        if next is None:
            if past is None:
                return None
            return args.default if args.default is not None else 'has passed'
        else:
            if cooldown is not None and not cooldown >= 0:
                return args.default if args.default else 'has passed'
            delta: str = format_timedelta(next.timestamp - timestamp)
            return (args.prefix or '') + delta + (args.suffix or '')
    return None


async def fieldSince(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() == 'since' and args.param is not None:
        timestamp: datetime = args.timestamp.replace(tzinfo=timezones.utc)
        npc: NextPastCooldown = parse_next_past_cooldown(args.param, timestamp)
        next: Optional[DateTime]
        past: Optional[DateTime]
        cooldown: float
        next, past, cooldown = npc
        if past is None:
            if next is None:
                return None
            return args.default if args.default is not None else 'is coming'
        else:
            if cooldown is not None and not cooldown <= 0:
                return args.default if args.default else 'is coming'
            delta: str = format_timedelta(timestamp - past.timestamp)
            return (args.prefix or '') + delta + (args.suffix or '')
    return None


async def fieldNext(args: CustomFieldArgs) -> Optional[str]:
    if args.field.lower() in ['next', 'future'] and args.param is not None:
        timestamp: datetime = args.timestamp.replace(tzinfo=timezones.utc)
        npc: NextPastCooldown = parse_next_past_cooldown(args.param, timestamp)
        next: Optional[DateTime]
        past: Optional[DateTime]
        cooldown: float
        next, past, cooldown = npc
        if next is None:
            if past is None:
                return None
            return args.default if args.default is not None else 'None'
        else:
            format: str = _24HourFormat if next.format24 else _12HourFormat
            timeStr: str = next.timestamp.strftime(format)
            return (args.prefix or '') + timeStr + (args.suffix or '')
    return None


async def fieldPrevious(args: CustomFieldArgs) -> Optional[str]:
    if (args.field.lower() in ['prev', 'previous', 'past']
            and args.param is not None):
        timestamp: datetime = args.timestamp.replace(tzinfo=timezones.utc)
        npc: NextPastCooldown = parse_next_past_cooldown(args.param, timestamp)
        next: Optional[DateTime]
        past: Optional[DateTime]
        cooldown: float
        next, past, cooldown = npc
        if past is None:
            if next is None:
                return None
            return args.default if args.default is not None else 'None'
        else:
            format: str = _24HourFormat if past.format24 else _12HourFormat
            timeStr: str = past.timestamp.strftime(format)
            return (args.prefix or '') + timeStr + (args.suffix or '')
    return None


def parse_date_string(string: str) -> Optional[DateTimeInstance]:
    match: Match[str] = re.fullmatch(_pattern, string, re.IGNORECASE)
    if match is None:
        return None
    g: Sequence[str] = match.groups()
    hour: int
    minute: int
    seconds: int = 0
    microseconds: int = 0
    is24Hour: bool
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
        hour = hour if hour != 12 else 0
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
    timezone: timezones.BaseTimeZone
    if g[13] is not None:
        if g[13].lower() not in timezones.abbreviations:
            return None
        timezone = timezones.abbreviations[g[13].lower()]
    else:
        timezone = timezones.utc
    timeOfDay: time = time(hour, minute, seconds, microseconds, timezone)
    dayofweek: Optional[int] = None
    date_: Optional[Date] = None
    if g[3] is not None:
        dayofweek = daysOfWeek[g[3].lower()]
    elif g[0] is not None and g[1] is not None:
        month = int(g[0])
        day = int(g[1])
        if g[2] is not None:
            year = int(g[2])
            try:
                date(year, month, day)
            except ValueError:
                return None
        else:
            year = None
            try:
                date(2000, month, day)
            except ValueError:
                return None
        date_ = Date(year, month, day)

    return DateTimeInstance(timeOfDay, dayofweek, date_, is24Hour)


def next_datetime(now: datetime,
                  timeOfDay: time,
                  dayofweek: Optional[int],
                  date_: Optional[Date],
                  is24Hour: bool) -> Optional[DateTime]:
    today: date
    if timeOfDay.tzinfo is not None:
        today = now.astimezone(timeOfDay.tzinfo).date()
    else:
        today = now.date()
    dt: datetime
    actualDate: date
    if date_ is not None:
        if date_.year is not None:
            dt = datetime.combine(date(*date_), timeOfDay)
            if dt > now:
                return DateTime(dt, is24Hour)
            else:
                return None
        ldate: List[int] = [today.year, date_.month, date_.day]
        # For February 29
        while True:
            try:
                actualDate = date(*ldate)
                break
            except ValueError:
                ldate[0] += 1
        dt = datetime.combine(actualDate, timeOfDay)
        if dt > now:
            return DateTime(dt, is24Hour)
        else:
            year: int = actualDate.year + 1
            # For February 29
            while True:
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year += 1
            return DateTime(datetime.combine(actualDate, timeOfDay), is24Hour)
    elif dayofweek is not None:
        daysToAdd: int = dayofweek - today.weekday()
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


def past_datetime(now: datetime,
                  timeOfDay: time,
                  dayofweek: Optional[int],
                  date_: Optional[Date],
                  is24Hour: bool) -> Optional[DateTime]:
    today: date
    if timeOfDay.tzinfo is not None:
        today = now.astimezone(timeOfDay.tzinfo).date()
    else:
        today = now.date()
    dt: datetime
    actualDate: date
    if date_ is not None:
        if date_.year is not None:
            dt = datetime.combine(date(*date_), timeOfDay)
            if dt <= now:
                return DateTime(dt, is24Hour)
            else:
                return None
        ldate: List[int] = [today.year, date_.month, date_.day]
        # For February 29
        while True:
            try:
                actualDate = date(*ldate)
                break
            except ValueError:
                ldate[0] -= 1
        dt = datetime.combine(actualDate, timeOfDay)
        if dt <= now:
            return DateTime(dt, is24Hour)
        else:
            year: int = actualDate.year - 1
            # For February 29
            while True:
                try:
                    actualDate = actualDate.replace(year=year)
                    break
                except ValueError:
                    year -= 1
            return DateTime(datetime.combine(actualDate, timeOfDay), is24Hour)
    elif dayofweek is not None:
        daysToAdd: int = dayofweek - today.weekday()
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


def parse_cooldown(string: str) -> Optional[Union[float, timedelta]]:
    match: Match[str] = re.fullmatch(_cooldownPattern, string.strip())
    if match is None:
        return None
    groups: Sequence[str] = match.groups()
    if groups[0] is not None:
        return float(groups[0]) / 100.0
    elif (groups[1] is not None
          or groups[2] is not None
          or groups[3] is not None
          or groups[4] is not None
          or groups[5] is not None):
        weeks: int = int(groups[1] or 0)
        days: int = int(groups[2] or 0)
        hours: int = int(groups[3] or 0)
        minutes: int = int(groups[4] or 0)
        seconds: int = int(groups[5] or 0)
        return timedelta(weeks=weeks, days=days, hours=hours,
                         minutes=minutes, seconds=seconds)
    return None


def test_cooldown(cooldown: Optional[Union[float, timedelta]],
                  past: datetime,
                  future: datetime,
                  now: datetime) -> float:
    if cooldown is None:
        return 0
    if now < past:
        return -math.inf
    if now > future:
        return math.inf
    cooldown_: timedelta
    if isinstance(cooldown, float):
        cooldown_ = (future - past) * cooldown
    elif isinstance(cooldown, timedelta):
        cooldown_ = cooldown
    else:
        return 0
    begindelta: timedelta = now - past
    enddelta: timedelta = future - now
    if begindelta <= cooldown_ and enddelta <= cooldown_:
        return math.nan
    elif begindelta >= cooldown_ and enddelta >= cooldown_:
        return 0
    elif begindelta <= cooldown_:
        return -1
    else:
        return 1


def parse_next_past_cooldown(times: str,
                             now: datetime) -> NextPastCooldown:
    cd: Optional[Union[float, timedelta]] = None
    instances: List[DateTimeInstance] = []
    i: int
    timeStr: str
    for i, timeStr in enumerate(times.split(',')):
        if i == 0:
            cd = parse_cooldown(timeStr)
            if cd is not None:
                continue
        instance: Optional[DateTimeInstance]
        instance = parse_date_string(timeStr.strip())
        if instance is not None:
            instances.append(instance)
    nextDts: List[Optional[DateTime]]
    pastDts: List[Optional[DateTime]]
    nextDts = [next_datetime(now, *inst) for inst in instances]
    pastDts = [past_datetime(now, *inst) for inst in instances]
    nextDatetimes: List[DateTime] = [dt for dt in nextDts if dt is not None]
    pastDatetimes: List[DateTime] = [dt for dt in pastDts if dt is not None]
    next: DateTime = min(nextDatetimes) if nextDatetimes else None
    past: DateTime = max(pastDatetimes) if pastDatetimes else None
    cooldown: Optional[float] = None
    if next is not None and past is not None:
        cooldown = test_cooldown(cd, past.timestamp, next.timestamp, now)
    return NextPastCooldown(next, past, cooldown)
