import datetime
import unittest

import pytz
from pandas import DataFrame

from brFinance.scraper.bacen.currency import Currency


class TestCurrency(unittest.TestCase):
    AVAILABLE_CURRENCIES_COLUMNS = ["Currency", "Code"]
    PRICE_COLUMNS = ["Tipo", "Moeda", "Compra", "Venda"]

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().setUpClass()

    def setUp(self):
        self.today = datetime.datetime.now(pytz.timezone("Brazil/East"))
        self.week_ago = self.today - datetime.timedelta(days=7)

        self.currency = Currency(currency_code=61, initial_date=self.week_ago.strftime("%d/%m/%Y"),
                                 final_date=self.today.strftime("%d/%m/%Y"))

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_available_currencies(self) -> None:
        df = self.currency.get_available_currencies()

        self.assertIsInstance(df, DataFrame, msg="Available currencies is not a Dataframe")

        self.assertGreater(len(df), 0, "Dataframe is empty")

        self.assertEqual(list(df.columns), TestCurrency.AVAILABLE_CURRENCIES_COLUMNS,
                         msg="Wrong columns inside dataframe")

    def test_get_all_currencies_prices_by_date(self) -> None:
        df = self.currency.get_all_currencies_prices_by_date(datetime.datetime(2021, 9, 3))

        self.assertIsInstance(df, DataFrame, msg="Today prices result is not a Dataframe")

        self.assertGreaterEqual(len(df), 0, "Dataframe is empty")

        self.assertEqual(list(df.columns), TestCurrency.PRICE_COLUMNS, msg="Wrong columns inside dataframe")

        # self.assertEqual(df.dtypes[2], "float64", msg="Buy column is not a float64")
        # self.assertEqual(df.dtypes[3], "float64", msg="Sell column is not a float64")

    def test_get_price(self) -> None:
        df = self.currency.get_price()

        self.assertIsInstance(df, DataFrame, msg="Price result is not a Dataframe")

        self.assertGreater(len(df), 0, "Dataframe is empty")

        print(list(df.columns))
        self.assertCountEqual(list(df.columns), TestCurrency.PRICE_COLUMNS, msg="Wrong columns inside dataframe")

        self.assertEqual(df.dtypes[2], "float64", msg="Buy column is not a float64")
        self.assertEqual(df.dtypes[3], "float64", msg="Sell column is not a float64")

    def test_assert_raises_for_invalid_date(self) -> None:
        self.assertRaises(AssertionError, Currency(currency_code=61, initial_date=self.today.strftime("%d/%m/%Y"),
                                                   final_date=self.week_ago.strftime("%d/%m/%Y")).get_price)

    def test_assert_raises_for_invalid_code(self) -> None:
        self.assertRaises(AssertionError, Currency(currency_code=300, initial_date=self.week_ago.strftime("%d/%m/%Y"),
                                                   final_date=self.today.strftime("%d/%m/%Y")).get_price)
