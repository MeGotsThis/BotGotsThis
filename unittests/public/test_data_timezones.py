import unittest
from datetime import datetime, timedelta
from source.data import timezones


class TestDataBasicTimeZone(unittest.TestCase):
    def setUp(self):
        self.timezone = timezones.BasicTimeZone(60, 'BASE')

    def test_zone_none(self):
        self.assertRaises(TypeError, timezones.BasicTimeZone, None)

    def test_zone_int_none(self):
        self.assertRaises(TypeError, timezones.BasicTimeZone, 0, None)

    def test_tzname(self):
        self.assertEqual(self.timezone.tzname(None), 'BASE')

    def test_utcoffset(self):
        self.assertEqual(self.timezone.utcoffset(None), timedelta(minutes=60))

    def test_dst(self):
        self.assertEqual(self.timezone.dst(None), timedelta())


class TestDataTimeZone(unittest.TestCase):
    def setUp(self):
        transitions = [
            timezones.Transition(-2147483648, 'START', 3600),
            timezones.Transition(86400 * 0, 'DAY1', 7200),
            timezones.Transition(86400 * 1, 'DAY2', 3600),
            timezones.Transition(86400 * 2, 'DAY3', 7200),
            timezones.Transition(86400 * 3, 'DAY4', 3600),
            timezones.Transition(2147483647, 'END', 3600),
            ]
        self.timezone = timezones.TimeZone('ZONE', transitions)

    def test_none(self):
        transitions = [timezones.Transition(0, 'START', 60)]
        self.assertRaises(TypeError, timezones.TimeZone, None, transitions)

    def test_str_none(self):
        self.assertRaises(TypeError, timezones.TimeZone, 'EMPTY', None)

    def test_no_transitions(self):
        self.assertRaises(ValueError, timezones.TimeZone, 'EMPTY', [])

    def test_zone(self):
        self.assertEqual(self.timezone.zone(), 'ZONE')

    def test_tzname_none_int(self):
        self.assertRaises(TypeError, self.timezone.tzname, 0)

    def test_utcoffset_none_int(self):
        self.assertRaises(TypeError, self.timezone.utcoffset, 0)

    def test_dst_none_int(self):
        self.assertRaises(TypeError, self.timezone.dst, 0)

    def test_tzname_none(self):
        self.assertEqual(self.timezone.tzname(None), 'START')

    def test_utcoffset_none(self):
        self.assertEqual(self.timezone.utcoffset(None), timedelta(minutes=60))

    def test_dst_none(self):
        self.assertEqual(self.timezone.dst(None), timedelta())

    def test_tzname_datetime(self):
        self.assertEqual(self.timezone.tzname(datetime(1969, 1, 1)), 'START')
        self.assertEqual(self.timezone.tzname(datetime(1970, 1, 1)), 'DAY1')
        self.assertEqual(self.timezone.tzname(datetime(1970, 1, 2)), 'DAY2')
        self.assertEqual(self.timezone.tzname(datetime(1970, 1, 3)), 'DAY3')
        self.assertEqual(self.timezone.tzname(datetime(1970, 1, 4)), 'DAY4')
        self.assertEqual(self.timezone.tzname(datetime(3000, 1, 1)), 'END')

    def test_utcoffset_datetime(self):
        self.assertEqual(self.timezone.utcoffset(datetime(1969, 1, 1)),
                         timedelta(minutes=60))
        self.assertEqual(self.timezone.utcoffset(datetime(1970, 1, 1)),
                         timedelta(minutes=120))
        self.assertEqual(self.timezone.utcoffset(datetime(1970, 1, 2)),
                         timedelta(minutes=60))
        self.assertEqual(self.timezone.utcoffset(datetime(1970, 1, 3)),
                         timedelta(minutes=120))
        self.assertEqual(self.timezone.utcoffset(datetime(1970, 1, 4)),
                         timedelta(minutes=60))
        self.assertEqual(self.timezone.utcoffset(datetime(3000, 1, 1)),
                         timedelta(minutes=60))

    def test_dst_datetime(self):
        self.assertEqual(self.timezone.dst(datetime(1969, 1, 1)), timedelta())
        self.assertEqual(self.timezone.dst(datetime(1970, 1, 1)),
                         timedelta(minutes=60))
        self.assertEqual(self.timezone.dst(datetime(1970, 1, 2)), timedelta())
        self.assertEqual(self.timezone.dst(datetime(1970, 1, 3)),
                         timedelta(minutes=60))
        self.assertEqual(self.timezone.dst(datetime(1970, 1, 4)), timedelta())
        self.assertEqual(self.timezone.dst(datetime(3000, 1, 1)), timedelta())
