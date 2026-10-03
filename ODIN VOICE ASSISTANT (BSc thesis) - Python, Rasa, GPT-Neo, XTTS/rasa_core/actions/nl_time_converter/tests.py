import unittest
from datetime import datetime, timedelta

from rasa_core.actions.nl_time_converter.nl_time_converter import parse_time_expression


class TestTimeParsing(unittest.TestCase):

    def test_today(self):
        result = parse_time_expression("today")
        expected = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_tomorrow(self):
        result = parse_time_expression("tomorrow")
        expected = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_tomorrow_night(self):
        result = parse_time_expression("tomorrow night")
        expected = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

    def test_specific_time(self):
        result = parse_time_expression("at ten PM")
        expected = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

    def test_two_days_from_now(self):
        result = parse_time_expression("two days from now")
        expected = datetime.now().replace(second=0, microsecond=0, minute=0, hour=0) + timedelta(days=2)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_next_week(self):
        result = parse_time_expression("next week")
        expected = datetime.now().replace(second=0, microsecond=0, minute=0, hour=0) + timedelta(weeks=1)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_next_monday(self):
        result = parse_time_expression("next Monday")
        today = datetime.today().replace(second=0, microsecond=0, minute=0, hour=0)
        target_weekday = 0  # Monday
        current_weekday = today.weekday()
        days_until_next = (target_weekday - current_weekday + 7) % 7
        if days_until_next == 0:
            days_until_next = 7
        expected = today + timedelta(days=days_until_next)
        expected = expected.replace(second=0, microsecond=0, minute=0, hour=0)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_in_two_hours(self):
        result = parse_time_expression("in two hours")
        expected = datetime.now().replace(second=0, microsecond=0, minute=0) + timedelta(hours=2)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

    def test_in_five_minutes(self):
        result = parse_time_expression("in five minutes")
        result = result.replace(microsecond=0, second=0)

        expected = datetime.now().replace(second=0, microsecond=0)
        expected += timedelta(minutes=5)

        self.assertEqual(result, expected)

    def test_next_friday(self):
        result = parse_time_expression("next Friday")
        today = datetime.today().replace(second=0, microsecond=0, minute=0, hour=0)
        target_weekday = 4  # Friday
        current_weekday = today.weekday()
        days_until_next = (target_weekday - current_weekday + 7) % 7
        if days_until_next == 0:
            days_until_next = 7
        expected = today + timedelta(days=days_until_next)
        expected = expected.replace(second=0, microsecond=0, minute=0, hour=0)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0, hour=0), expected)

    def test_tomorrow_night_at_10_pm(self):
        result = parse_time_expression("tomorrow night at 10 PM")
        expected = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

    def test_next_monday_at_two_am(self):
        result = parse_time_expression("next Monday at two AM")
        today = datetime.today().replace(second=0, microsecond=0, minute=0, hour=0)
        target_weekday = 0  # Monday
        current_weekday = today.weekday()
        days_until_next = (target_weekday - current_weekday + 7) % 7
        if days_until_next == 0:
            days_until_next = 7
        expected = today + timedelta(days=days_until_next)
        expected = expected.replace(hour=2, minute=0, second=0, microsecond=0)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

    def test_tomorrow_at_five_pm(self):
        result = parse_time_expression("tomorrow at 5 PM")
        expected = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(result.replace(microsecond=0, second=0, minute=0), expected)

if __name__ == '__main__':
    unittest.main()
