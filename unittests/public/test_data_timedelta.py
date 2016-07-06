import unittest
from datetime import timedelta
from source.data import timedelta as mtimedelta


class TestDataTimeDelta(unittest.TestCase):
    def test_format_none(self):
        self.assertRaises(TypeError, mtimedelta.format, None)

    def test_format_one_second(self):
        self.assertEqual(mtimedelta.format(timedelta(seconds=1)), '1 second')

    def test_format_two_seconds(self):
        self.assertEqual(mtimedelta.format(timedelta(seconds=2)), '2 seconds')

    def test_format_sixty_seconds(self):
        self.assertEqual(mtimedelta.format(timedelta(seconds=60)), '1 minute')

    def test_format_one_minute(self):
        self.assertEqual(mtimedelta.format(timedelta(minutes=1)), '1 minute')

    def test_format_two_minutes(self):
        self.assertEqual(mtimedelta.format(timedelta(minutes=2)), '2 minutes')

    def test_format_sixty_minutes(self):
        self.assertEqual(mtimedelta.format(timedelta(minutes=60)), '1 hour')

    def test_format_one_hour(self):
        self.assertEqual(mtimedelta.format(timedelta(hours=1)), '1 hour')

    def test_format_two_hours(self):
        self.assertEqual(mtimedelta.format(timedelta(hours=2)), '2 hours')

    def test_format_twenty_four_hours(self):
        self.assertEqual(mtimedelta.format(timedelta(hours=24)), '1 day')

    def test_format_one_day(self):
        self.assertEqual(mtimedelta.format(timedelta(days=1)), '1 day')

    def test_format_two_days(self):
        self.assertEqual(mtimedelta.format(timedelta(days=2)), '2 days')

    def test_format_seven_days(self):
        self.assertEqual(mtimedelta.format(timedelta(days=7)), '7 days')

    def test_format_second_minute_hour_day(self):
        self.assertEqual(
            mtimedelta.format(
                timedelta(seconds=1, minutes=1, hours=1, days=1)),
            '1 day, 1 hour, 1 minute, 1 second')
