from abc import ABCMeta, abstractmethod
from contextlib import closing
from datetime import datetime, timedelta, tzinfo
from typing import Dict, NamedTuple, Optional, Sequence
import configparser
import os
import sqlite3

Transition = NamedTuple('Transition',
                        [('start', int),  # in unix timestamp
                         ('abbreviation', str),
                         ('offset', int)])  # in seconds

ZERO = timedelta(0)


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
        self.__offset = timedelta(minutes=offset)  # type: timedelta
        self.__name = name  # type: str
    
    def zone(self) -> str:
        return self.__name
    
    def tzname(self, dt: Optional[datetime]) -> str:
        return self.__name
    
    def utcoffset(self, dt: Optional[datetime]) -> timedelta:  # type: ignore --
        return timedelta(minutes=self.__offset.seconds // 60)
    
    def dst(self, dt: Optional[datetime]) -> timedelta:  # type: ignore --
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
        self.__zone = zone  # type: str
        self._transitions = transitions  # type: Sequence[Transition]
    
    def zone(self) -> str:
        return self.__zone
    
    def tzname(self, dt: Optional[datetime]) -> str:
        if dt is None:
            return self._transitions[0].abbreviation
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())  # type: int
        transistion = self._transitions[0]  # type: Transition
        for t in self._transitions[::-1]:  # --type: Transition
            if unixTime >= t.start:
                transistion = t
                break
        return transistion.abbreviation
    
    def utcoffset(self, dt: Optional[datetime]) -> timedelta:  # type: ignore --
        if dt is None:
            return timedelta(minutes=self._transitions[0].offset // 60)
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())  # type: int
        transistion = self._transitions[0]  # type: Transition
        for t in self._transitions[::-1]:  # --type: Transition
            if unixTime >= t.start:
                transistion = t
                break
        return timedelta(minutes=transistion.offset // 60)
     
    def dst(self, dt: Optional[datetime]) -> timedelta:  # type: ignore --
        if dt is None:
            return ZERO
        if not isinstance(dt, datetime):
            raise TypeError()
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())  # type: int
        transistion = self._transitions[0]  # type: Transition
        for t in self._transitions[::-1]:  # --type: Transition
            if unixTime >= t.start:
                transistion = t
                break
        delta = transistion.offset - self._transitions[0].offset  # type: int
        return timedelta(minutes=delta // 60)

utc = BasicTimeZone(0, 'UTC')
unixEpoch = datetime(1970, 1, 1, 0, 0, 0, 0)

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
    ]  # type: List[BaseTimeZone]

if os.path.isfile('config.ini'):
    _ini = configparser.ConfigParser()
    _ini.read('config.ini')
    with sqlite3.connect(
        _ini['TIMEZONEDB']['timezonedb'], detect_types=True) as _connection, \
            closing(_connection.cursor()) as _cursor:
        _cursor.execute('''
SELECT abbreviation, gmt_offset FROM timezone
    WHERE time_start >= 2114380800
    AND abbreviation NOT IN ('CST', 'CDT', 'AMT', 'AST', 'GST', 'IST',
                             'KST', 'BST', 'UTC')
    GROUP BY abbreviation
UNION ALL SELECT abbreviation, gmt_offset FROM timezone
    WHERE time_start=2147483647 AND
    zone_id IN (382, 75, 294, 281, 190, 211, 159)''')
        # For the abbreviation conflicts of: CST, CDT, AMT, AST, GST, IST, KST,
        # BST
        # I have choosen: America/Chicago, America/Boa_Vista,
        # America/Puerto_Rico, Asia/Muscat, Asia/Jerusalem, Asia/Seoul,
        #  Europe/London
        for _row in _cursor:
            timezones.append(BasicTimeZone(_row[1] // 60, _row[0]))
        _zones = {}  # type: Dict[int, str]
        _transitions = {}  # type: Dict[int, List[Transition]]
        _cursor.execute('SELECT zone_id, zone_name FROM zone ORDER BY zone_id')
        for _row in _cursor:
            _zones[_row[0]] = _row[1]
            _transitions[_row[0]] = []
        _cursor.execute('SELECT zone_id, abbreviation, time_start, gmt_offset '
                        "FROM timezone WHERE abbreviation != 'UTC' "
                        'ORDER BY zone_id, time_start')
        for _row in _cursor:
            _transitions[_row[0]].append(Transition(_row[2], _row[1], _row[3]))
        for _z in _zones:
            timezones.append(TimeZone(_zones[_z], _transitions[_z]))
    del _ini, _connection, _cursor, _row, _z, _zones, _transitions

abbreviations = {tz.zone().lower(): tz for tz in timezones}

del closing, configparser, os, sqlite3, tzinfo
