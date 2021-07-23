import re
from dataclasses import dataclass
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


@dataclass
class SearchENET:
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx according to the input
    parameters

    ...

    Attributes
    ----------
    SEARCH_CATEGORY_LIST : list
        List of categories code accepted by the class
    DELAY : int
        Timeout (in seconds) for page to load
    cod_cvm : int
        CVM company code
    category : int
        Category code

    Methods
    -------
    cod_cvm_list()
        Returns a dataframe of all CVM codes and Company names
    search()
        Returns dataframe of search results including cod_cvm, report's url, etc.
    """

    SEARCH_CATEGORY_LIST = [21, 39]
    DELAY = 1

    def __init__(self, cod_cvm: int, category: int, driver: webdriver = None):
        """
        Parameters
        ----------
        cod_cvm : int
            CVM company code
        category : int
            Category code
        driver : webdriver
            Optional parameter for webdriver created by user

        Raises
        ------
        AssertionError
            If cvm code does not exist or an invalid category code is passed
        """

        self.driver = driver

        assert self._check_cod_cvm_exist(cod_cvm), "CVM code not found"
        assert self._check_category_exist(category), \
            f"Invalid category value. Available categories are: {SearchENET.SEARCH_CATEGORY_LIST} "

        self.cod_cvm = cod_cvm
        self.category = category

    def _check_cod_cvm_exist(self, cod_cvm: int) -> bool:
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

        codigos_cvm_available = self.cod_cvm_list()
        cod_cvm_exists = str(cod_cvm) in [str(cod_cvm_aux) for cod_cvm_aux in codigos_cvm_available['codCVM'].values]
        return cod_cvm_exists

    def _check_category_exist(self, category: int) -> bool:
        """Check if Category code is supported by brFinance

        Parameters
        ----------
        category : int
            Category code

        Returns
        -------
        bool
            True if category code is accepted, otherwise False
        """

        return category in SearchENET.SEARCH_CATEGORY_LIST

    def _instantiate_driver(self) -> webdriver:
        """Returns a driver object

        Returns
        -------
        selenium.webdriver
            webdriver created for searching
        """

        if self.driver is None:
            return Browser.run_chromedriver()

        return self.driver

    def _extract_data_from_search(self, initial_date: str, final_date: str) -> Tuple[pd.DataFrame, Any]:
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
        wait = WebDriverWait(driver, SearchENET.DELAY)

        driver.get(f"https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx?codigoCVM={self.cod_cvm}")

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
                                           f"@data-option-array-index='{self.category}']"
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

        if self.driver is None:
            driver.quit()

        return df, table

    def cod_cvm_list(self) -> pd.DataFrame:
        """Returns a dataframe of all CVM codes and Company names

        Returns
        -------
        pandas.Dataframe
            Dataframe of all CVM codes and company names
        """

        driver = self._instantiate_driver()
        wait = WebDriverWait(driver, SearchENET.DELAY)

        driver.get("https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx")

        # Wait until page is loaded and get all companies data
        while True:
            try:
                companies_result_id = "hdnEmpresas"
                wait.until(EC.presence_of_element_located((By.ID, companies_result_id)))
                html_data = driver.find_element_by_id(companies_result_id).get_attribute("value")
                break
            except TimeoutException:
                print("[LOG]: Waiting CVM codes")

        # Selecting company name and CVM code
        list_cod_cvm = re.findall(r"(?<=_)(.*?)(?=\')", html_data)
        list_nome_emp = re.findall(r"(?<=-)(.*?)(?=\')", html_data)

        # Adding selected information to a Dataframe
        df = pd.DataFrame(list(zip(list_cod_cvm, list_nome_emp)), columns=['codCVM', 'nome_empresa'])
        df['codCVM'] = pd.to_numeric(df['codCVM'])

        if self.driver is None:
            driver.quit()

        return df

    @property
    def search(self) -> pd.DataFrame:
        """Returns dataframe of search results including cod_cvm, report's url, etc.

        Returns
        -------
        pandas.Dataframe
            Dataframe of search results
        """

        initial_date = '01012010'
        final_date = datetime.today().strftime('%d%m%Y')

        df, table = self._extract_data_from_search(initial_date, final_date)

        # Cleaning data for CVM code and reference date
        df["Código CVM"] = self.cod_cvm
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
