from bot import utils

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, tzinfo
from typing import Dict, List, NamedTuple, Optional, Sequence, cast

from source import database


class Transition(NamedTuple):
    start: int  # in unix timestamp
    abbreviation: str
    offset: int  # in seconds


ZERO: timedelta = timedelta(0)


class BaseTimeZone(tzinfo, metaclass=ABCMeta):
    @abstractmethod
    def zone(self) -> str:
        return 'zone'


class BasicTimeZone(BaseTimeZone):
    """Fixed offset in minutes east from UTC."""
    __slots__ = ('__offset', '__name')
    
    def __init__(self,
                 offset: int,
                 name: str) -> None:
        if not isinstance(offset, int):
            raise TypeError()
        if not isinstance(name, str):
            raise TypeError()
        self.__offset: timedelta = timedelta(minutes=offset)
        self.__name: str = name
    
    def zone(self) -> str:
        return self.__name
    
    def tzname(self, dt: Optional[datetime]) -> str:
        return self.__name
    
    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        return timedelta(minutes=self.__offset.total_seconds() // 60)
    
    def dst(self, dt: Optional[datetime]) -> timedelta:
        return ZERO


class TimeZone(BaseTimeZone):
    """Fixed offset in minutes east from UTC."""
    __slots__ = ('__zone', '_transitions')
    
    def __init__(self,
                 zone: str,
                 transitions: Sequence[Transition]) -> None:
        if not isinstance(zone, str):
            raise TypeError()
        if not isinstance(transitions, Sequence):
            raise TypeError()
        if not transitions:
            raise ValueError()
        self.__zone: str = zone
        self._transitions: Sequence[Transition] = transitions
    
    def zone(self) -> str:
        return self.__zone
    
    def tzname(self, dt: Optional[datetime]) -> str:
        if dt is None:
            return self._transitions[0].abbreviation
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime: int
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion: Transition = self._transitions[0]
        t: Transition
        for t in self._transitions[::-1]:
            if unixTime >= t.start:
                transistion = t
                break
        return transistion.abbreviation
    
    def utcoffset(self, dt: Optional[datetime]) -> timedelta:
        if dt is None:
            return timedelta(minutes=self._transitions[0].offset // 60)
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime: int
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion: Transition = self._transitions[0]
        t: Transition
        for t in self._transitions[::-1]:
            if unixTime >= t.start:
                transistion = t
                break
        return timedelta(minutes=transistion.offset // 60)
     
    def dst(self, dt: Optional[datetime]) -> timedelta:
        if dt is None:
            return ZERO
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime: int
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion: Transition = self._transitions[0]
        t: Transition
        for t in self._transitions[::-1]:
            if unixTime >= t.start:
                transistion = t
                break
        delta: int = transistion.offset - self._transitions[0].offset
        return timedelta(minutes=delta // 60)


utc: BasicTimeZone = BasicTimeZone(0, 'UTC')
unixEpoch: datetime = datetime(1970, 1, 1, 0, 0, 0, 0)

timezones: List[BaseTimeZone] = []

abbreviations: Dict[str, BaseTimeZone] = {}


async def load_timezones():
    global timezones, abbreviations
    print('{time} Loading Time Zones'.format(time=utils.now()))
    timezones = [
        utc,
        BasicTimeZone(0, 'UTC±00:00'),
        BasicTimeZone(0, 'UTC+00:00'),
        BasicTimeZone(60, 'UTC+01:00'),
        BasicTimeZone(120, 'UTC+02:00'),
        BasicTimeZone(180, 'UTC+03:00'),
        BasicTimeZone(240, 'UTC+04:00'),
        BasicTimeZone(300, 'UTC+05:00'),
        BasicTimeZone(360, 'UTC+06:00'),
        BasicTimeZone(420, 'UTC+07:00'),
        BasicTimeZone(480, 'UTC+08:00'),
        BasicTimeZone(540, 'UTC+09:00'),
        BasicTimeZone(600, 'UTC+10:00'),
        BasicTimeZone(660, 'UTC+11:00'),
        BasicTimeZone(720, 'UTC+12:00'),
        BasicTimeZone(-0, 'UTC-00:00'),
        BasicTimeZone(-60, 'UTC-01:00'),
        BasicTimeZone(-120, 'UTC-02:00'),
        BasicTimeZone(-180, 'UTC-03:00'),
        BasicTimeZone(-240, 'UTC-04:00'),
        BasicTimeZone(-300, 'UTC-05:00'),
        BasicTimeZone(-360, 'UTC-06:00'),
        BasicTimeZone(-420, 'UTC-07:00'),
        BasicTimeZone(-480, 'UTC-08:00'),
        BasicTimeZone(-540, 'UTC-09:00'),
        BasicTimeZone(-600, 'UTC-10:00'),
        BasicTimeZone(-660, 'UTC-11:00'),
        BasicTimeZone(-720, 'UTC-12:00'),
        BasicTimeZone(0, 'UTC±0000'),
        BasicTimeZone(0, 'UTC+0000'),
        BasicTimeZone(60, 'UTC+0100'),
        BasicTimeZone(120, 'UTC+0200'),
        BasicTimeZone(180, 'UTC+0300'),
        BasicTimeZone(240, 'UTC+0400'),
        BasicTimeZone(300, 'UTC+0500'),
        BasicTimeZone(360, 'UTC+0600'),
        BasicTimeZone(420, 'UTC+0700'),
        BasicTimeZone(480, 'UTC+0800'),
        BasicTimeZone(540, 'UTC+0900'),
        BasicTimeZone(600, 'UTC+1000'),
        BasicTimeZone(660, 'UTC+1100'),
        BasicTimeZone(720, 'UTC+1200'),
        BasicTimeZone(-0, 'UTC-0000'),
        BasicTimeZone(-60, 'UTC-0100'),
        BasicTimeZone(-120, 'UTC-0200'),
        BasicTimeZone(-180, 'UTC-0300'),
        BasicTimeZone(-240, 'UTC-0400'),
        BasicTimeZone(-300, 'UTC-0500'),
        BasicTimeZone(-360, 'UTC-0600'),
        BasicTimeZone(-420, 'UTC-0700'),
        BasicTimeZone(-480, 'UTC-0800'),
        BasicTimeZone(-540, 'UTC-0900'),
        BasicTimeZone(-600, 'UTC-1000'),
        BasicTimeZone(-660, 'UTC-1100'),
        BasicTimeZone(-720, 'UTC-1200'),
        BasicTimeZone(0, 'UTC±00'),
        BasicTimeZone(0, 'UTC+00'),
        BasicTimeZone(60, 'UTC+01'),
        BasicTimeZone(120, 'UTC+02'),
        BasicTimeZone(180, 'UTC+03'),
        BasicTimeZone(240, 'UTC+04'),
        BasicTimeZone(300, 'UTC+05'),
        BasicTimeZone(360, 'UTC+06'),
        BasicTimeZone(420, 'UTC+07'),
        BasicTimeZone(480, 'UTC+08'),
        BasicTimeZone(540, 'UTC+09'),
        BasicTimeZone(600, 'UTC+10'),
        BasicTimeZone(660, 'UTC+11'),
        BasicTimeZone(720, 'UTC+12'),
        BasicTimeZone(-0, 'UTC-00'),
        BasicTimeZone(-60, 'UTC-01'),
        BasicTimeZone(-120, 'UTC-02'),
        BasicTimeZone(-180, 'UTC-03'),
        BasicTimeZone(-240, 'UTC-04'),
        BasicTimeZone(-300, 'UTC-05'),
        BasicTimeZone(-360, 'UTC-06'),
        BasicTimeZone(-420, 'UTC-07'),
        BasicTimeZone(-480, 'UTC-08'),
        BasicTimeZone(-540, 'UTC-09'),
        BasicTimeZone(-600, 'UTC-10'),
        BasicTimeZone(-660, 'UTC-11'),
        BasicTimeZone(-720, 'UTC-12'),
    ]

    _db: database.Database
    db: database.DatabaseTimeZone
    async with database.get_database(database.Schema.TimeZone) as _db:
        db = cast(database.DatabaseTimeZone, _db)
        row: tuple
        async for row in db.timezone_names():
            timezones.append(BasicTimeZone(row[1] // 60, row[0]))

        zones: Dict[int, str] = {}
        transitions: Dict[int, List[Transition]] = {}
        async for row in db.zones():
            zones[row[0]] = row[1]
            transitions[row[0]] = []

        for row in await db.zone_transitions():
            transitions[row[0]].append(Transition(row[2], row[1], row[3]))
        z: int
        for z in zones:
            timezones.append(TimeZone(zones[z], transitions[z]))
        abbreviations = {tz.zone().lower(): tz for tz in timezones}

    print('{time} Loaded Time Zones'.format(time=utils.now()))
