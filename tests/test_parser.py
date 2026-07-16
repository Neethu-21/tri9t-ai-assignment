import unittest
import re


class TestParser(unittest.TestCase):

    def test_heading_detection(self):
        line = "2.1 Device Description"
        self.assertTrue(re.match(r'^\d+(\.\d+)*\.', line))

    def test_non_heading(self):
        line = "This is normal body text."
        self.assertFalse(re.match(r'^\d+(\.\d+)*\.', line))

    def test_heading_level(self):
        number = "3.2.1"
        level = number.count(".") + 1
        self.assertEqual(level, 3)


if __name__ == "__main__":
    unittest.main()