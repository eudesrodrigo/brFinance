import os
import pickle
import re
from pathlib import Path
from typing import Tuple, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from brFinance.scraper.cvm.financial_report import FinancialReport
from brFinance.scraper.cvm.search import SearchDFP, SearchITR
from brFinance.utils.browser import Browser


class Company:
    """
    An instance of a Company can fetch useful information about Financial Reports, Social Capital and Registration Data
    """

    def __init__(self, cvm_code: int):
        """
        Parameters
        ----------
        cvm_code : int
            CVM company code
        """
        self.cvm_code = cvm_code

    def _save_files(self, driver, report_info) -> Dict:
        document_number = re.search(r"(?<=\Documento=)(.*?)(?=&)", report_info['linkView']).group()

        # Create folder and save reports locally
        path_save_reports = f'{os.getcwd()}/reports'
        report_file = f'{path_save_reports}/{document_number}.plk'
        Path(path_save_reports).mkdir(exist_ok=True)

        # Check if report is available locally, otherwise scrape it.
        if Path(report_file).exists():
            with open(report_file, 'rb') as load_report:
                report_obj = pickle.load(load_report)
                print("Carregado localmente!")
        else:
            report_obj = FinancialReport(link=report_info["linkView"], driver=driver).get_report()
            with open(report_file, 'wb') as save_report:
                pickle.dump(report_obj, save_report)

        return report_obj

    def get_social_capital_data(self) -> pd.DataFrame:
        """
        Returns a dataframe including number of preference or ordinal shares for a company

        Returns
        -------
        pandas.Dataframe
            Dataframe with Social Capital Data
        """
        url = f"http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp?CodCVM={self.cvm_code}"
        df = pd.DataFrame()
        try:
            html_content = requests.get(url).content.decode("utf8")

            social_capital_data = BeautifulSoup(html_content, "lxml").find("div",
                                                                           attrs={"id": "divComposicaoCapitalSocial"})

            df = pd.read_html(str(social_capital_data), thousands='.')[0]
            df.columns = ["Type", "Quantity"]
        except Exception as exp:
            print(exp)

        return df

    def get_registration_data(self) -> pd.DataFrame:
        """
        Returns a dataframe including useful information about company's registration data

        Returns
        -------
        pandas.Dataframe
            Dataframe with Registration Data
        """
        url = "http://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
        company_registration_data = pd.DataFrame()

        try:
            df = pd.read_csv(url, sep=";", encoding="latin")
            company_registration_data = df[df["CD_CVM"] == self.cvm_code]
        except Exception as exp:
            print(exp)

        return company_registration_data

    def get_all_reports(self, driver: webdriver = Browser.run_chromedriver()) -> Tuple[Dict, Dict]:
        """
        Returns two dictionaries including financial report data

        Parameters
        ----------
        driver : webdriver
            Optional parameter for webdriver created by user

        Returns
        -------
        Dict
            Dictionary with annual reports
        Dict
            Dictionary with quarter reports
        """
        annual_reports = self.get_annual_reports(driver)
        quarter_reports = self.get_quarterly_reports(driver)

        return annual_reports, quarter_reports

    def get_annual_reports(self, driver: webdriver = Browser.run_chromedriver()) -> Dict:
        """
        Returns a dictionary including annual financial report data

        Parameters
        ----------
        driver : webdriver
            Optional parameter for webdriver created by user

        Returns
        -------
        Dict
            Dictionary with annual reports
        """
        search_annual_reports = SearchDFP(driver=driver).search(self.cvm_code)
        reports = {}

        for index, report_info in search_annual_reports.iterrows():
            report_obj = self._save_files(driver, report_info)
            reports[report_obj["reference_date"]] = report_obj["reports"]

        driver.quit()

        return reports

    def get_quarterly_reports(self, driver: webdriver = Browser.run_chromedriver()) -> Dict:
        """
        Returns a dictionary including quarter financial report data

        Parameters
        ----------
        driver : webdriver
            Optional parameter for webdriver created by user

        Returns
        -------
        Dict
            Dictionary with quarter reports
        """
        search_quarter_reports = SearchITR(driver=driver).search(self.cvm_code)
        reports = {}

        for index, report_info in search_quarter_reports.iterrows():
            report_obj = self._save_files(driver, report_info)
            reports[report_obj["reference_date"]] = report_obj["reports"]

        driver.quit()

        return reports
