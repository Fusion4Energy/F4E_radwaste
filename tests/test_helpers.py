import unittest

from f4e_radwaste.helpers import format_time_seconds_to_str


class HelpersTests(unittest.TestCase):
    def test_format_time_seconds_to_str(self):
        # Test cases
        test_cases = [
            (1, "1.00s"),
            (59, "59.00s"),
            (3600, "1.00h"),
            (7200, "2.00h"),
            (86400, "24.00h"),
            (172800, "48.00h"),
            (2592000, "30.00d"),
            (5184000, "60.00d"),
            (31536000, "1.00y"),
            (63072000, "2.00y"),
            (6307200000, "200.00y"),
        ]

        # Run tests
        for seconds, expected_result in test_cases:
            result = format_time_seconds_to_str(seconds)
            self.assertEqual(result, expected_result)
