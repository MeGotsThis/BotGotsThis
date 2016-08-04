import math
import unittest
from datetime import datetime, time, timedelta
from source.data import timezones
from source.data.message import Message
from source.data.timedelta import format
from source.public.custom import countdown
from unittest.mock import patch
from unittests.public.test_custom import TestCustomField


class TestCustomCountdownParse(unittest.TestCase):
    def test(self):
        self.assertIsNone(countdown.parse_date_string(''))

    def test_time_of_day(self):
        self.assertEqual(
            countdown.parse_date_string('0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('00:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('12:34'),
            countdown.DateTimeInstance(time(12, 34, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('23:59'),
            countdown.DateTimeInstance(time(23, 59, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertIsNone(countdown.parse_date_string('24:00'))
        self.assertIsNone(countdown.parse_date_string('0:60'))
        self.assertIsNone(countdown.parse_date_string('000:00'))
        self.assertIsNone(countdown.parse_date_string('0:000'))

    def test_time_of_day_seconds(self):
        self.assertEqual(
            countdown.parse_date_string('0:00:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('0:00:59'),
            countdown.DateTimeInstance(time(0, 0, 59, 0, timezones.utc),
                                       None, None, True))
        self.assertIsNone(countdown.parse_date_string('0:00:60'))

    def test_time_of_day_seconds_microseconds(self):
        self.assertEqual(
            countdown.parse_date_string('0:00:00.000000'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('0:00:00.000001'),
            countdown.DateTimeInstance(time(0, 0, 0, 1, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('0:00:00.999999'),
            countdown.DateTimeInstance(time(0, 0, 0, 999999, timezones.utc),
                                       None, None, True))
        self.assertIsNone(countdown.parse_date_string('0:00:00.0000000'))
        self.assertIsNone(countdown.parse_date_string('0:00:00.9999999'))

    def test_time_of_day_meridiem(self):
        self.assertEqual(
            countdown.parse_date_string('12:00AM'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('1:23PM'),
            countdown.DateTimeInstance(time(13, 23, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('01:23am'),
            countdown.DateTimeInstance(time(1, 23, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('11:59pm'),
            countdown.DateTimeInstance(time(23, 59, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertIsNone(countdown.parse_date_string('12:00BM'))
        self.assertIsNone(countdown.parse_date_string('0:00AM'))
        self.assertIsNone(countdown.parse_date_string('0:60AM'))
        self.assertIsNone(countdown.parse_date_string('13:00AM'))
        self.assertIsNone(countdown.parse_date_string('000:00AM'))
        self.assertIsNone(countdown.parse_date_string('0:000AM'))

    def test_time_of_day_seconds_meridiem(self):
        self.assertEqual(
            countdown.parse_date_string('12:00:00AM'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('12:00:59PM'),
            countdown.DateTimeInstance(time(12, 0, 59, 0, timezones.utc),
                                       None, None, False))
        self.assertIsNone(countdown.parse_date_string('0:00:60AM'))

    def test_time_of_day_seconds_microseconds_meridiem(self):
        self.assertEqual(
            countdown.parse_date_string('12:00:00.000000AM'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('12:00:00.000001PM'),
            countdown.DateTimeInstance(time(12, 0, 0, 1, timezones.utc),
                                       None, None, False))
        self.assertEqual(
            countdown.parse_date_string('12:00:00.999999AM'),
            countdown.DateTimeInstance(time(0, 0, 0, 999999, timezones.utc),
                                       None, None, False))
        self.assertIsNone(countdown.parse_date_string('0:00:00.0000000AM'))
        self.assertIsNone(countdown.parse_date_string('0:00:00.9999999PM'))

    def test_time_of_day_timezone(self):
        self.assertEqual(
            countdown.parse_date_string('0:00 UTC'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('0:00 utc'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('0:00 UTC-00:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       None, None, True))
        self.assertEqual(
            countdown.parse_date_string('12:00AM UTC+12:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.abbreviations['utc+12:00']),
                None, None, False))
        self.assertIsNone(countdown.parse_date_string('0:00 ABC'))

    def test_day_of_week_time_of_day(self):
        self.assertEqual(
            countdown.parse_date_string('Sunday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Monday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.MONDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Tuesday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.TUESDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Wednesday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.WEDNESDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Thursday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.THURSDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Friday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.FRIDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Saturday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SATURDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('SUNDAY 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('sunday 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Sun 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Mon 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.MONDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Tue 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.TUESDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Wed 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.WEDNESDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Thu 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.THURSDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Fri 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.FRIDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('Sat 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SATURDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('SUN 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertEqual(
            countdown.parse_date_string('sun 0:00'),
            countdown.DateTimeInstance(time(0, 0, 0, 0, timezones.utc),
                                       countdown.SUNDAY, None, True))
        self.assertIsNone(countdown.parse_date_string('abc 0:00'))

    def test_month_day_time_of_day(self):
        self.assertEqual(
            countdown.parse_date_string('1/1 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(None, 1, 1), True))
        self.assertEqual(
            countdown.parse_date_string('12-31 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(None, 12, 31), True))
        self.assertEqual(
            countdown.parse_date_string('2/29 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(None, 2, 29), True))
        self.assertIsNone(countdown.parse_date_string('1/32 0:00'))
        self.assertIsNone(countdown.parse_date_string('13/1 0:00'))
        self.assertIsNone(countdown.parse_date_string('2/30 0:00'))

    def test_month_day_year_time_of_day(self):
        self.assertEqual(
            countdown.parse_date_string('1/1/2000 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(2000, 1, 1), True))
        self.assertEqual(
            countdown.parse_date_string('12-31-2016 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(2016, 12, 31), True))
        self.assertEqual(
            countdown.parse_date_string('2/29/2000 0:00'),
            countdown.DateTimeInstance(
                time(0, 0, 0, 0, timezones.utc),
                None, countdown.Date(2000, 2, 29), True))
        self.assertIsNone(countdown.parse_date_string('1/32/2015 0:00'))
        self.assertIsNone(countdown.parse_date_string('13/1/2014 0:00'))
        self.assertIsNone(countdown.parse_date_string('2/30/2000 0:00'))
        self.assertIsNone(countdown.parse_date_string('2/29/2001 0:00'))

    def test_many(self):
        self.assertEqual(
            countdown.parse_date_string('6/15/2000 10:48:23.987654PM UTC'),
            countdown.DateTimeInstance(
                time(22, 48, 23, 987654, timezones.utc),
                None, countdown.Date(2000, 6, 15), False))
        self.assertEqual(
            countdown.parse_date_string('Wed 16:49:31.456187 UTC'),
            countdown.DateTimeInstance(time(16, 49, 31, 456187, timezones.utc),
                                       countdown.WEDNESDAY, None, True))
        self.assertIsNone(
            countdown.parse_date_string('UTC 16:49:31.456187 Wed'))
        self.assertIsNone(
            countdown.parse_date_string('UTC 10:48:23.987654PM 6/15/2000'))


class TestCustomCountdownNextDatetime(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1, tzinfo=timezones.utc)

    def test_time_of_day(self):
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, None, True),
            countdown.DateTime(datetime(2000, 1, 2, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 1, 0, 0, timezones.utc),
                                    None, None, False),
            countdown.DateTime(datetime(2000, 1, 1, 0, 1, 0, 0, timezones.utc),
                               False))
        self.assertEqual(
            countdown.next_datetime(self.now,
                                    time(23, 59, 59, 999999, timezones.utc),
                                    None, None, False),
            countdown.DateTime(datetime(2000, 1, 1, 23, 59, 59, 999999,
                                        timezones.utc),
                               False))

    def test_time_of_day_day_of_week(self):
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.SUNDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 2, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.MONDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 3, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.TUESDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 4, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.WEDNESDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 5, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.THURSDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 6, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.FRIDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 7, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.SATURDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 8, 0, 0, 0, 0, timezones.utc),
                               True))

    def test_time_of_day_month_day(self):
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(None, 1, 1), True),
            countdown.DateTime(datetime(2001, 1, 1, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(None, 12, 31), True),
            countdown.DateTime(datetime(2000, 12, 31, 0, 0, 0, 0,
                                        timezones.utc),
                               True))

    def test_time_of_day_year_month_day(self):
        self.assertIsNone(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(2000, 1, 1), True))
        self.assertEqual(
            countdown.next_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(2000, 12, 31), True),
            countdown.DateTime(datetime(2000, 12, 31, 0, 0, 0, 0,
                                        timezones.utc),
                               True))


class TestCustomCountdownPastDatetime(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1, tzinfo=timezones.utc)

    def test_time_of_day(self):
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, None, True),
            countdown.DateTime(datetime(2000, 1, 1, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 1, 0, 0, timezones.utc),
                                    None, None, False),
            countdown.DateTime(datetime(1999, 12, 31, 0, 1, 0, 0,
                                        timezones.utc),
                               False))
        self.assertEqual(
            countdown.past_datetime(self.now,
                                    time(23, 59, 59, 999999, timezones.utc),
                                    None, None, False),
            countdown.DateTime(datetime(1999, 12, 31, 23, 59, 59, 999999,
                                        timezones.utc),
                               False))

    def test_time_of_day_day_of_week(self):
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.SUNDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 26, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.MONDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 27, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.TUESDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 28, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.WEDNESDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 29, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.THURSDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 30, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.FRIDAY, None, True),
            countdown.DateTime(datetime(1999, 12, 31, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    countdown.SATURDAY, None, True),
            countdown.DateTime(datetime(2000, 1, 1, 0, 0, 0, 0,
                                        timezones.utc),
                               True))

    def test_time_of_day_month_day(self):
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(None, 1, 1), True),
            countdown.DateTime(datetime(2000, 1, 1, 0, 0, 0, 0,
                                        timezones.utc),
                               True))
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(None, 12, 31), True),
            countdown.DateTime(datetime(1999, 12, 31, 0, 0, 0, 0,
                                        timezones.utc),
                               True))

    def test_time_of_day_year_month_day(self):
        self.assertEqual(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(2000, 1, 1), True),
            countdown.DateTime(datetime(2000, 1, 1, 0, 0, 0, 0, timezones.utc),
                               True))
        self.assertIsNone(
            countdown.past_datetime(self.now, time(0, 0, 0, 0, timezones.utc),
                                    None, countdown.Date(2000, 12, 31), True))


class TestCustomCountdownParseCooldown(unittest.TestCase):
    def test_percent(self):
        self.assertEqual(countdown.parse_cooldown('0%'), 0.0)
        self.assertEqual(countdown.parse_cooldown('100%'), 1.0)
        self.assertEqual(countdown.parse_cooldown('42%'), 0.42)
        self.assertIsNone(countdown.parse_cooldown('101%'))
        self.assertIsNone(countdown.parse_cooldown('1000%'))
        self.assertIsNone(countdown.parse_cooldown('-0%'))

    def test_weeks(self):
        self.assertEqual(countdown.parse_cooldown('0w'), timedelta(weeks=0))
        self.assertEqual(countdown.parse_cooldown('1w'), timedelta(weeks=1))
        self.assertEqual(countdown.parse_cooldown('2w'), timedelta(weeks=2))
        self.assertEqual(countdown.parse_cooldown('15961w'),
                         timedelta(weeks=15961))

    def test_days(self):
        self.assertEqual(countdown.parse_cooldown('0d'), timedelta(days=0))
        self.assertEqual(countdown.parse_cooldown('1d'), timedelta(days=1))
        self.assertEqual(countdown.parse_cooldown('2d'), timedelta(days=2))
        self.assertEqual(countdown.parse_cooldown('89156d'),
                         timedelta(days=89156))

    def test_hours(self):
        self.assertEqual(countdown.parse_cooldown('0h'), timedelta(hours=0))
        self.assertEqual(countdown.parse_cooldown('1h'), timedelta(hours=1))
        self.assertEqual(countdown.parse_cooldown('23h'), timedelta(hours=23))
        self.assertIsNone(countdown.parse_cooldown('24h'))

    def test_minutes(self):
        self.assertEqual(countdown.parse_cooldown('0m'), timedelta(minutes=0))
        self.assertEqual(countdown.parse_cooldown('1m'), timedelta(minutes=1))
        self.assertEqual(countdown.parse_cooldown('59m'),
                         timedelta(minutes=59))
        self.assertIsNone(countdown.parse_cooldown('60m'))

    def test_seconds(self):
        self.assertEqual(countdown.parse_cooldown('0s'), timedelta(seconds=0))
        self.assertEqual(countdown.parse_cooldown('1s'), timedelta(seconds=1))
        self.assertEqual(countdown.parse_cooldown('59s'),
                         timedelta(seconds=59))
        self.assertIsNone(countdown.parse_cooldown('60s'))

    def test_multiple(self):
        self.assertEqual(countdown.parse_cooldown('1w1d'),
                         timedelta(weeks=1, days=1))
        self.assertEqual(countdown.parse_cooldown('1d1h'),
                         timedelta(days=1, hours=1))
        self.assertEqual(countdown.parse_cooldown('1h1m'),
                         timedelta(hours=1, minutes=1))
        self.assertEqual(countdown.parse_cooldown('1m1s'),
                         timedelta(minutes=1, seconds=1))
        self.assertIsNone(countdown.parse_cooldown('1d1w'))
        self.assertIsNone(countdown.parse_cooldown('1h1d'))
        self.assertIsNone(countdown.parse_cooldown('1m1h'))
        self.assertIsNone(countdown.parse_cooldown('1s1m'))
        self.assertIsNone(countdown.parse_cooldown('1s1m1h1d1w'))
        self.assertEqual(countdown.parse_cooldown('0w0d0h0m0s'), timedelta())
        self.assertEqual(
            countdown.parse_cooldown('1w1d1h1m1s'),
            timedelta(weeks=1, days=1, hours=1, minutes=1, seconds=1))
        self.assertEqual(
            countdown.parse_cooldown('2w13d23h59m59s'),
            timedelta(weeks=3, days=6, hours=23, minutes=59, seconds=59))


class TestCustomCountdownTestCooldown(unittest.TestCase):
    def test(self):
        self.assertEqual(
            countdown.test_cooldown(None,
                                    datetime(2000, 1, 1, 0, 0, 0, 0),
                                    datetime(2000, 1, 2, 0, 0, 0, 0),
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            0)

    def test_timedelta(self):
        duration = timedelta(hours=1)
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 0, 0, 0)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 59, 59, 999999)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 1, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 12, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 23, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 23, 0, 0, 1)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 2, 0, 0, 0, 0)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)

    def test_timedelta_over_half(self):
        duration = timedelta(hours=20)
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 0, 0, 0)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 3, 59, 59, 999999)),
            -1)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 4, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 12, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 20, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 20, 0, 0, 1)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 2, 0, 0, 0, 0)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)

    def test_timedelta_over_full(self):
        duration = timedelta(days=2)
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 0, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 12, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 2, 0, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)

    def test_float(self):
        duration = 1 / 24
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 0, 0, 0)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 59, 59, 999999)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 1, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 12, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 23, 0, 0, 0)),
            0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 23, 0, 0, 1)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 2, 0, 0, 0, 0)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)

    def test_float_over_half(self):
        duration = 20 / 24
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 0, 0, 0, 0)),
            -1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 3, 59, 59, 999999)),
            -1)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 4, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 12, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 20, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 1, 20, 0, 0, 1)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 2, 0, 0, 0, 0)),
            1)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)

    def test_float_over_full(self):
        duration = 2.0
        past = datetime(2000, 1, 1, 0, 0, 0, 0)
        future = datetime(2000, 1, 2, 0, 0, 0, 0)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(1999, 12, 31, 0, 0, 0, 0)),
            -math.inf)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 0, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 1, 12, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        test = countdown.test_cooldown(duration, past, future,
                                       datetime(2000, 1, 2, 0, 0, 0, 0))
        self.assertTrue(math.isnan(test), test)
        self.assertEqual(
            countdown.test_cooldown(duration, past, future,
                                    datetime(2000, 1, 3, 0, 0, 0, 0)),
            math.inf)


class TestCustomCountdownParseNextPastCooldown(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2000, 1, 1, tzinfo=timezones.utc)

    def test_blank(self):
        times = ''
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(None, None, None))

    def test(self):
        times = 'abcd'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(None, None, None))

    def test_cooldown(self):
        times = '1h'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(None, None, None))

    def test_single_exact_next(self):
        times = '1/2/2000 0:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
                None, None))

    def test_single_exact_past(self):
        times = '12/31/1999 12:00AM'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                None,
                countdown.DateTime(
                    datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), False),
                None))

    def test_multiple_exact(self):
        times = '12/31/1999 12:00AM,1/2/2000 0:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), False),
                0))

    def test_hour_minute(self):
        times = '0:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(2000, 1, 1, 0, 0, tzinfo=timezones.utc), True),
                0))

    def test_day_of_week(self):
        times = 'Sun 0:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 26, 0, 0, tzinfo=timezones.utc), True),
                0))

    def test_month_day(self):
        times = '1/1 0:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2001, 1, 1, 0, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(2000, 1, 1, 0, 0, tzinfo=timezones.utc), True),
                0))

    def test_multiple(self):
        times = '12/25/1999 6:00PM,1/31 0:00,7:00AM,19:00,Wed 20:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 7, 0, tzinfo=timezones.utc), False),
                countdown.DateTime(
                    datetime(1999, 12, 31, 19, 0, tzinfo=timezones.utc), True),
                0))

    def test_multiple_2(self):
        times = '6:00AM,18:00,12/31 23:00,1/1 1:00AM'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 1, 0, tzinfo=timezones.utc), False),
                countdown.DateTime(
                    datetime(1999, 12, 31, 23, 0, tzinfo=timezones.utc), True),
                0))

    def test_hour_minute_cooldown(self):
        times = '0:00,1h'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(2000, 1, 1, 0, 0, tzinfo=timezones.utc), True),
                0))

    def test_cooldown_hour_minute(self):
        times = '4h,12:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 12, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 12, 0, tzinfo=timezones.utc), True),
                0))

    def test_cooldown_hour_minute_early_cooldown(self):
        times = '4h,23:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 23, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 23, 0, tzinfo=timezones.utc), True),
                -1))

    def test_cooldown_hour_minute_late_cooldown(self):
        times = '4h,1:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 1, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 1, 0, tzinfo=timezones.utc), True),
                1))

    def test_cooldown_hour_minute_overlap_cooldown(self):
        times = '18h,12:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 12, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 12, 0, tzinfo=timezones.utc), True),
                math.nan))

    def test_cooldown_hour_minute_multiple(self):
        times = '50%,9:00,21:00'
        self.assertEqual(
            countdown.parse_next_past_cooldown(times, self.now),
            countdown.NextPastCooldown(
                countdown.DateTime(
                    datetime(2000, 1, 1, 9, 0, tzinfo=timezones.utc), True),
                countdown.DateTime(
                    datetime(1999, 12, 31, 21, 0, tzinfo=timezones.utc), True),
                -1))


class TestCustomCountdownFieldCountdown(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='countdown', param='')

        patcher = patch(
            'source.public.custom.countdown.parse_next_past_cooldown',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_parse = patcher.start()
        self.mock_parse.return_value = countdown.NextPastCooldown(None, None,
                                                                  None)

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(countdown.fieldCountdown(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_none_time(self):
        self.args = self.args._replace(param=None)
        self.assertIsNone(countdown.fieldCountdown(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_invalid_time(self):
        self.assertIsNone(countdown.fieldCountdown(self.args))
        self.assertTrue(self.mock_parse.called)

    def test_default(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)

    def test_default_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)

    def test_default_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldCountdown(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_default_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldCountdown(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_time(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         '[' + format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)) + ']')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_not_cooldown(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            0)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.inf)
        self.assertEqual(countdown.fieldCountdown(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_cooldown(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -math.inf)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.nan)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldCountdown(self.args), 'has passed')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldCountdown(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldCountdown(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)


class TestCustomCountdownFieldSince(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='since', param='')

        patcher = patch(
            'source.public.custom.countdown.parse_next_past_cooldown',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_parse = patcher.start()
        self.mock_parse.return_value = countdown.NextPastCooldown(None, None,
                                                                  None)

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(countdown.fieldSince(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_none_time(self):
        self.args = self.args._replace(param=None)
        self.assertIsNone(countdown.fieldSince(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_invalid_time(self):
        self.assertIsNone(countdown.fieldSince(self.args))
        self.assertTrue(self.mock_parse.called)

    def test_default(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)

    def test_default_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)

    def test_default_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldSince(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_default_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldSince(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_time(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldSince(self.args),
                         '[' + format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)) + ']')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_not_cooldown(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            0)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -math.inf)
        self.assertEqual(countdown.fieldSince(self.args),
                         format(timedelta(days=1)))
        self.assertTrue(self.mock_parse.called)

    def test_cooldown(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.inf)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.nan)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldSince(self.args), 'is coming')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldSince(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldSince(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)


class TestCustomCountdownFieldNext(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='next', param='')

        patcher = patch(
            'source.public.custom.countdown.parse_next_past_cooldown',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_parse = patcher.start()
        self.mock_parse.return_value = countdown.NextPastCooldown(None, None,
                                                                  None)

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(countdown.fieldNext(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_none_time(self):
        self.args = self.args._replace(param=None)
        self.assertIsNone(countdown.fieldNext(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_invalid_time(self):
        self.assertIsNone(countdown.fieldNext(self.args))
        self.assertTrue(self.mock_parse.called)

    def test_default(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldNext(self.args), 'None')
        self.assertTrue(self.mock_parse.called)

    def test_default_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldNext(self.args), 'None')
        self.assertTrue(self.mock_parse.called)

    def test_default_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldNext(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_default_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldNext(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_time(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_12_hour(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), False),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 12:00AM UTC')
        self.assertTrue(self.mock_parse.called)

    def test_future(self):
        self.args = self.args._replace(field='future')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '[01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC]')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown(self):
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            0)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.inf)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.nan)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -math.inf)
        self.assertEqual(countdown.fieldNext(self.args),
                         '01/02/2000 00:00 UTC')
        self.assertTrue(self.mock_parse.called)


class TestCustomCountdownFieldPrevious(TestCustomField):
    def setUp(self):
        super().setUp()
        self.args = self.args._replace(field='previous', param='')

        patcher = patch(
            'source.public.custom.countdown.parse_next_past_cooldown',
            autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_parse = patcher.start()
        self.mock_parse.return_value = countdown.NextPastCooldown(None, None,
                                                                  None)

    def test(self):
        self.args = self.args._replace(field='')
        self.assertIsNone(countdown.fieldPrevious(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_none_time(self):
        self.args = self.args._replace(param=None)
        self.assertIsNone(countdown.fieldPrevious(self.args))
        self.assertFalse(self.mock_parse.called)

    def test_invalid_time(self):
        self.assertIsNone(countdown.fieldPrevious(self.args))
        self.assertTrue(self.mock_parse.called)

    def test_default(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldPrevious(self.args), 'None')
        self.assertTrue(self.mock_parse.called)

    def test_default_prefix_suffix(self):
        self.args = self.args._replace(prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldPrevious(self.args), 'None')
        self.assertTrue(self.mock_parse.called)

    def test_default_default(self):
        self.args = self.args._replace(default='Kappa')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldPrevious(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_default_default_prefix_suffix(self):
        self.args = self.args._replace(default='Kappa',
                                       prefix='[', suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            None,
            None)
        self.assertEqual(countdown.fieldPrevious(self.args), 'Kappa')
        self.assertTrue(self.mock_parse.called)

    def test_time(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_12_hour(self):
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), False),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 12:00AM UTC')
        self.assertTrue(self.mock_parse.called)

    def test_past(self):
        self.args = self.args._replace(field='past')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_prev(self):
        self.args = self.args._replace(field='prev')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix(self):
        self.args = self.args._replace(prefix='[')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '[12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_prefix_blank(self):
        self.args = self.args._replace(prefix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix(self):
        self.args = self.args._replace(suffix=']')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC]')
        self.assertTrue(self.mock_parse.called)

    def test_time_suffix_blank(self):
        self.args = self.args._replace(suffix='')
        self.mock_parse.return_value = countdown.NextPastCooldown(
            None,
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            None)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)

    def test_cooldown(self):
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            0)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.inf)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            1)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            math.nan)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -1)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
        self.mock_parse.reset_mock()
        self.mock_parse.return_value = countdown.NextPastCooldown(
            countdown.DateTime(
                datetime(2000, 1, 2, 0, 0, tzinfo=timezones.utc), True),
            countdown.DateTime(
                datetime(1999, 12, 31, 0, 0, tzinfo=timezones.utc), True),
            -math.inf)
        self.assertEqual(countdown.fieldPrevious(self.args),
                         '12/31/1999 00:00 UTC')
        self.assertTrue(self.mock_parse.called)
