import datetime

import pandas as pd

from brFinance.scraper.bacen.search import SearchAvailableCurrencies, SearchCurrencyPrice, SearchTodayCurrencyPrices


class Currency:
    """
    Perform webscraping on Brazilian Central Bank page to get information about currency and it's value
    """

    def __init__(self, currency_code: int, initial_date: str, final_date: str):
        """
        Parameters
        ----------
        currency_code : int
            Currency code according to available currencies method
        initial_date: str
            Ex: 01/01/2021
        final_date: str
            Ex: 30/07/2021
        """
        self.currency_code = currency_code
        self.initial_date = datetime.datetime.strptime(initial_date, "%d/%m/%Y")
        self.final_date = datetime.datetime.strptime(final_date, "%d/%m/%Y")

    @staticmethod
    def get_available_currencies() -> pd.DataFrame:
        """
        Returns
        -------
        pandas.Dataframe
            Dataframe with available currencies and respective codes
        """
        return SearchAvailableCurrencies().get_available_currencies()

    @staticmethod
    def get_today_prices() -> pd.DataFrame:
        """
        Returns
        -------
        pandas.Dataframe
            Dataframe with today prices of all currencies in respect to Brazilian Real
        """
        return SearchTodayCurrencyPrices().get_today_prices()

    def get_price(self) -> pd.DataFrame:
        """
        Returns
        -------
        pandas.Dataframe
            Dataframe with prices of a specific currency in respect to Brazilian Real
        """
        return SearchCurrencyPrice(self.currency_code, self.initial_date, self.final_date).get_data()
