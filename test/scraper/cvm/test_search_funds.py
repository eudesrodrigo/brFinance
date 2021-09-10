from datetime import datetime
import unittest

from pandas import DataFrame

from brFinance.scraper.cvm.search import SearchFundsData


class TestSearchFundsData(unittest.TestCase):
    COLUMNS = ['cnpj_fundo',
               'dt_comptc',
               'vl_total',
               'vl_quota',
               'vl_patrim_liq',
               'captc_dia',
               'resg_dia',
               'nr_cotst']

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().setUpClass()

    def setUp(self):
        self.funds = SearchFundsData(reference_date=datetime(2021, 8, 1))

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_daily_data(self):
        df_funds_daily_data = self.funds.get_daily_data()

        self.assertCountEqual(list(df_funds_daily_data.columns),
                                   TestSearchFundsData.COLUMNS,
                                   msg="Wrong columns inside funds daily data dataframe.")
