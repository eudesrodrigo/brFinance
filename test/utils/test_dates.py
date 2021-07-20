import unittest
from datetime import date

from brFinance.utils.dates import Dates


class TestUtilsDates(unittest.TestCase):
    """
    tests for class Dates from module utils
    """
    
    def test_previous_quarter_end_date(self):
        """
        Tests method previous_quarter_end_date
        """

        date_obj = Dates(date(2021, 7, 12))
        quarter_end = date_obj.previous_quarter_end_date
        self.assertIsInstance(quarter_end, date, msg="Wrong return type for previous_quarter_end_date.")

        self.assertEqual(quarter_end, date(2021, 6, 30), msg=f"Return date to previous quarter end of 2021-7-12 is wrong:{quarter_end}")