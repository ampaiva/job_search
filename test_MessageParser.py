from unittest import TestCase

from parameterized import parameterized

from MessageParser import MessageParser


class TestMessageParser(TestCase):
    @parameterized.expand([
        ("Sat, 27 Apr 2024 21:22:59 +0000", 1714252979.0),
        ("Wed, 17 Apr 2024 19:50:46 +0000 (UTC)", 1713383446.0),
        ("Mon, 15 Apr 2024 13:42:46 -0700 (MST)", 1713213766.0),
    ])
    def test_date(self, date_string, expected_timestamp):
        message = {"payload": {"headers":
                                   [{"name": "Date", "value": date_string}]
                               }
                   }
        parser = MessageParser(message)
        timestamp = parser.date.timestamp()
        self.assertEqual(timestamp, expected_timestamp)
