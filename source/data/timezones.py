from contextlib import closing
import configparser
import datetime
import sqlite3

ZERO = datetime.timedelta(0)

class BasicTimeZone(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""
    __slots__ = ('__offset', '__name')
    
    def __init__(self, offset, name):
        self.__offset = datetime.timedelta(minutes=offset)
        self.__name = name
    
    def zone(self):
        return self.__name
    
    def tzname(self, dt):
        return self.__name
    
    def utcoffset(self, dt):
        return self.__offset
    
    def dst(self, dt):
        return ZERO

class TimeZone(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""
    __slots__ = ('__zone', '_transitions')
    
    def __init__(self, zone, transitions):
        self.__zone = zone
        self._transitions = transitions
    
    def zone(self):
        return self.__zone
    
    def tzname(self, dt):
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion = self._transitions[0]
        for t in self._transitions[::-1]:
            if unixTime >= t[0]:
                transistion = t
                break
        return transistion[1]
    
    def utcoffset(self, dt):
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion = self._transitions[0]
        for t in self._transitions[::-1]:
            if unixTime >= t[0]:
                transistion = t
                break
        return datetime.timedelta(seconds=transistion[2])
     
    def dst(self, dt):
        unixTime = int((dt.replace(tzinfo=None) - unixEpoch).total_seconds())
        transistion = self._transitions[0]
        for t in self._transitions[::-1]:
            if unixTime >= t[0]:
                transistion = t
                break
        delta = transistion[2] - self._transitions[0][2]
        return datetime.timedelta(seconds=delta)

utc = BasicTimeZone(0,'UTC')
unixEpoch = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)

timezones = [
    utc,
    BasicTimeZone(0,'UTC+0:00'),
    BasicTimeZone(60,'UTC+1:00'),
    BasicTimeZone(120,'UTC+2:00'),
    BasicTimeZone(180,'UTC+3:00'),
    BasicTimeZone(240,'UTC+4:00'),
    BasicTimeZone(300,'UTC+5:00'),
    BasicTimeZone(360,'UTC+6:00'),
    BasicTimeZone(420,'UTC+7:00'),
    BasicTimeZone(480,'UTC+8:00'),
    BasicTimeZone(540,'UTC+9:00'),
    BasicTimeZone(600,'UTC+10:00'),
    BasicTimeZone(660,'UTC+11:00'),
    BasicTimeZone(720,'UTC+12:00'),
    BasicTimeZone(-0,'UTC-0:00'),
    BasicTimeZone(-60,'UTC-1:00'),
    BasicTimeZone(-120,'UTC-2:00'),
    BasicTimeZone(-180,'UTC-3:00'),
    BasicTimeZone(-240,'UTC-4:00'),
    BasicTimeZone(-300,'UTC-5:00'),
    BasicTimeZone(-360,'UTC-6:00'),
    BasicTimeZone(-420,'UTC-7:00'),
    BasicTimeZone(-480,'UTC-8:00'),
    BasicTimeZone(-540,'UTC-9:00'),
    BasicTimeZone(-600,'UTC-10:00'),
    BasicTimeZone(-660,'UTC-11:00'),
    BasicTimeZone(-720,'UTC-12:00'),
    ]

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
    # For the abbreviation conflicts of: CST, CDT, AMT, AST, GST, IST, KST, BST
    # I have choosen: America/Chicago, America/Boa_Vista, America/Puerto_Rico,
    # Asia/Muscat, Asia/Jerusalem, Asia/Seoul, Europe/London
    for _row in _cursor:
        timezones.append(BasicTimeZone(_row[1] // 60, _row[0]))
    _zones = {}
    _transitions = {}
    _cursor.execute('SELECT zone_id, zone_name FROM zone ORDER BY zone_id')
    for _row in _cursor:
        _zones[_row[0]] = _row[1]
        _transitions[_row[0]] = []
    _cursor.execute('SELECT zone_id, abbreviation, time_start, gmt_offset '
                    "FROM timezone WHERE abbreviation != 'UTC' "
                    'ORDER BY zone_id, time_start')
    for _row in _cursor:
        _transitions[_row[0]].append((_row[2], _row[1], _row[3]))
    for _z in _zones:
        timezones.append(TimeZone(_zones[_z], _transitions[_z]))

abbreviations = {tz.zone().lower(): tz for tz in timezones}

del _ini, _connection, _cursor, _row, _z, _zones, _transitions
del closing, configparser, datetime, sqlite3
