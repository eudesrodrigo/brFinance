import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Any

import lxml.html as LH
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from brFinance.utils.browser import Browser


class Search(ABC):
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx
    """

    DELAY: int = 1
    cvm_code_df: pd.DataFrame = None
    cvm_code: int = None
    driver: webdriver = None

    def check_cvm_code_exists(self, cod_cvm: int) -> bool:
        """Check if CVM code exists

        Parameters
        ----------
        cod_cvm : int
            CVM company code

        Returns
        -------
        bool
            True if cvm code exist, otherwise False
        """

        cvm_codes_available = self.get_cvm_codes()
        cvm_code_exists = str(cod_cvm) in [str(cod_cvm_aux) for cod_cvm_aux in cvm_codes_available['codCVM'].values]
        return cvm_code_exists

    def _instantiate_driver(self) -> webdriver:
        """Returns a driver object

        Returns
        -------
        selenium.webdriver
            webdriver created for searching
        """

        if self.driver is None: return Browser.run_chromedriver()

        return self.driver

    def _fetch_data(self, cvm_code: int, category: int, initial_date: str, final_date: str) -> Tuple[pd.DataFrame, Any]:
        """Returns dataframe and html document from search

        Parameters
        ----------
        initial_date : str
            Initial date for search
        final_date : str
            Final date for search

        Returns
        -------
        pandas.Dataframe
            Dataframe containing search results
        lxml object
            Object containing html data from search
        """

        driver = self._instantiate_driver()
        wait = WebDriverWait(driver, Search.DELAY)

        driver.get(f"https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx?codigoCVM={cvm_code}")

        # Wait until page is loaded and click Categories button
        while True:
            try:
                category_button_id = 'cboCategorias_chosen'
                wait.until(EC.presence_of_element_located((By.ID, category_button_id)))
                driver.find_element_by_id(category_button_id).click()
                break
            except (TimeoutException, ElementClickInterceptedException):
                print("[LOG]: Waiting for Categories button")

        # Wait until page is loaded and select category from user input
        while True:
            try:
                category_selection_xpath = f"//html/body/form[1]/div[3]/div/fieldset/div[""5]/div[1]/div/div/ul/li[" \
                                           f"@data-option-array-index='{category}']"
                wait.until(EC.presence_of_element_located((By.XPATH, category_selection_xpath)))
                driver.find_element_by_xpath(category_selection_xpath).click()
                break
            except (TimeoutException, ElementClickInterceptedException):
                print("[LOG]: Waiting for category dropdown menu")

        # Wait until page is loaded and click Period button
        while True:
            try:
                period_button_xpath = "//html/body/form[1]/div[3]/div/fieldset/div[4]/div[1]/label[4]"
                wait.until(EC.presence_of_element_located((By.XPATH, period_button_xpath)))
                driver.find_element_by_xpath(period_button_xpath).click()
                break
            except (TimeoutException, ElementClickInterceptedException):
                print("[LOG]: Waiting for period button")

        # Wait until page is loaded and send keys for initial date
        while True:
            try:
                period_init_id = "txtDataIni"
                wait.until(EC.presence_of_element_located((By.ID, period_init_id)))
                driver.find_element_by_id(period_init_id).send_keys(initial_date)
                break
            except TimeoutException:
                print("[LOG]: Waiting for initial date input")

        # Wait until page is loaded and send keys for end date
        while True:
            try:
                period_end_id = "txtDataFim"
                wait.until(EC.presence_of_element_located((By.ID, period_end_id)))
                driver.find_element_by_id(period_end_id).send_keys(final_date)
                break
            except TimeoutException:
                print("[LOG]: Waiting for final date input")

        # Wait until page is loaded and click on Consult button
        while True:
            try:
                consult_button_id = "btnConsulta"
                wait.until(EC.presence_of_element_located((By.ID, consult_button_id)))
                driver.find_element_by_id(consult_button_id).click()
                break
            except (TimeoutException, ElementClickInterceptedException):
                print("[LOG]: Waiting for consult button")

        # Wait html table load the results (grdDocumentos)
        while True:
            try:
                results_xpath = "//table[@id='grdDocumentos']/tbody//tr"
                wait.until(EC.presence_of_element_located((By.XPATH, results_xpath)))
                table_html = str(driver.find_element_by_id('grdDocumentos').get_attribute("outerHTML"))
                break
            except TimeoutException:
                print("[LOG]: Waiting for results")

        table = LH.fromstring(table_html)
        df = pd.read_html(table_html)[0]

        if self.driver is None: driver.quit()

        return df, table

    def _clean_data(self, df, table):

        # Cleaning data for CVM code and reference date
        df["Código CVM"] = self.cvm_code
        df['Data Referência'] = df['Data Referência'].str.split(' ', 1).str[1]
        df['Data Referência'] = pd.to_datetime(df["Data Referência"], format="%d/%m/%Y", errors="coerce")

        # Creating a collumn for document visualization link
        link_view = []
        for expression in table.xpath("//tr/td/i[1]/@onclick"):
            link_view.append("https://www.rad.cvm.gov.br/ENET/" + re.findall("(?<=\')(.*?)(?=\')", expression)[0])
        df["linkView"] = link_view

        # Creating a collumn for document download link
        link_download = []
        for expression in table.xpath("//tr/td/i[2]/@onclick"):
            data = expression.split(",")
            num_sequencia = re.findall("(?<=\')(.*?)(?=\')", data[0])
            num_versao = re.findall("(?<=\')(.*?)(?=\')", data[1])
            num_protocolo = re.findall("(?<=\')(.*?)(?=\')", data[2])
            desc_tipo = re.findall("(?<=\')(.*?)(?=\')", data[3])
            link_download.append(f"https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&"
                                 f"numSequencia={num_sequencia}&"
                                 f"numVersao={num_versao}&"
                                 f"numProtocolo={num_protocolo}&"
                                 f"descTipo={desc_tipo}&"
                                 f"CodigoInstituicao=1")
        df["linkDownload"] = link_download

        # Filtering for documents which Status is Active
        df = df.drop(df[df["Status"] != "Ativo"].index)

        # Deleting Actions column
        del df["Ações"]

        return df

    def get_cvm_codes(self) -> pd.DataFrame:
        """Returns a dataframe of all CVM codes and Company names

        Returns
        -------
        pandas.Dataframe
            Dataframe of all CVM codes and company names
        """
        if Search.cvm_code_df is not None: return Search.cvm_code_df

        driver = self._instantiate_driver()
        wait = WebDriverWait(driver, Search.DELAY)

        driver.get("https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx")

        # Wait until page is loaded and get all companies data
        while True:
            try:
                companies_result_id = "hdnEmpresas"
                wait.until(EC.presence_of_element_located((By.ID, companies_result_id)))
                html_data = driver.find_element_by_id(companies_result_id).get_attribute("value")
                if len(html_data) == 0:
                    continue
                break
            except TimeoutException:
                print("[LOG]: Waiting CVM codes")

        # Selecting company name and CVM code
        list_cod_cvm = re.findall(r"(?<=_)(.*?)(?=\')", html_data)
        list_nome_emp = re.findall(r"(?<=-)(.*?)(?=\')", html_data)

        # Adding selected information to a Dataframe
        df = pd.DataFrame(list(zip(list_cod_cvm, list_nome_emp)), columns=['codCVM', 'nome_empresa'])
        df['codCVM'] = pd.to_numeric(df['codCVM'])

        Search.cvm_code_df = df

        if self.driver is None: driver.quit()

        return Search.cvm_code_df

    @abstractmethod
    def search(self, cvm_code: int, initial_date: str, final_date: str) -> pd.DataFrame:
        """
        Returns dataframe of search results including cod_cvm, report's url, etc.

        Parameters
        ----------
        cvm_code : int
            CVM company code
        initial_date: str
            Ex: 01012010 for 01/01/2010
        final_date: str
            Ex 30072021 for 30/07/2021

        Returns
        -------
        pandas.Dataframe
            Dataframe of search results
        """
        pass


class SearchDFP(Search):
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx for category
    "Demonstração Financeira Padronizada"
    """

    def __init__(self, driver: webdriver = None):
        """
        Parameters
        ----------
        driver : webdriver
            Optional parameter for webdriver created by user
        """

        self.driver = driver
        self.category = 21

    def search(self,
               cvm_code: int,
               initial_date: str = '01012010',
               final_date: str = datetime.today().strftime('%d%m%Y')) -> pd.DataFrame:
        assert self.check_cvm_code_exists(cvm_code), "CVM code not found"

        df, table = self._fetch_data(cvm_code, self.category, initial_date, final_date)

        df = self._clean_data(df, table)

        return df


class SearchITR(Search):
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx for category
    "Informações Trimestrais"
    """

    def __init__(self, driver: webdriver = None):
        """
        Parameters
        ----------
        driver : webdriver
            Optional parameter for webdriver created by user
        """

        self.driver = driver
        self.category = 39

    def search(self,
               cvm_code: int,
               initial_date: str = '01012010',
               final_date: str = datetime.today().strftime('%d%m%Y')) -> pd.DataFrame:
        assert self.check_cvm_code_exists(cvm_code), "CVM code not found"

        df, table = self._fetch_data(cvm_code, self.category, initial_date, final_date)

        df = self._clean_data(df, table)

        return df
