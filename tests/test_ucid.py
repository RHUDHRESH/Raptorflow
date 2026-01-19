import unittest
from datetime import datetime
import re

def generate_ucid(sequence_number):
    """
    Generates a Unique Customer ID in the format RF-YYYY-XXXX
    """
    year = datetime.now().year
    return f"RF-{year}-{sequence_number:04d}"

class TestUCIDGeneration(unittest.TestCase):
    def test_format(self):
        ucid = generate_ucid(1)
        self.assertTrue(re.match(r"^RF-\d{4}-\d{4}$", ucid))
        self.assertEqual(ucid[:3], "RF-")
        self.assertEqual(ucid[3:7], str(datetime.now().year))
        self.assertEqual(ucid[8:], "0001")

    def test_sequence(self):
        self.assertEqual(generate_ucid(10), f"RF-{datetime.now().year}-0010")
        self.assertEqual(generate_ucid(999), f"RF-{datetime.now().year}-0999")
        self.assertEqual(generate_ucid(1234), f"RF-{datetime.now().year}-1234")

if __name__ == "__main__":
    unittest.main()
