import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Any

import lxml.html as LH
import pandas as pd
from selenium import webdriver

from brFinance.utils.browser import Browser


class Search(ABC):
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx
    """

    DELAY: int = 1
    cvm_code_df: pd.DataFrame = None
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

        driver.get(f"https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx?codigoCVM={cvm_code}")

        # Wait until page is loaded and click Period button
        while True:
            try:
                period_button_xpath = "//html/body/form[1]/div[3]/div/fieldset/div[4]/div[1]/label[4]"
                #driver.find_element_by_xpath(period_button_xpath).click()
                driver.find_element_by_id("rdPeriodo").click()
                break
            except Exception:
                print("[LOG]: Waiting for period button")
                time.sleep(1)

        # Wait until page is loaded and send keys for initial date
        while True:
            try:
                period_init_id = "txtDataIni"
                driver.find_element_by_id(period_init_id).send_keys(initial_date)
                break
            except Exception:
                print("[LOG]: Waiting for initial date input")
                time.sleep(1)

        # Wait until page is loaded and send keys for end date
        while True:
            try:
                period_end_id = "txtDataFim"
                driver.find_element_by_id(period_end_id).send_keys(final_date)
                break
            except Exception:
                print("[LOG]: Waiting for final date input")
                time.sleep(1)

        # Wait until page is loaded and click Categories button
        while True:
            try:
                category_button_id = 'cboCategorias_chosen'
                driver.find_element_by_id(category_button_id).click()
                break
            except Exception:
                print("[LOG]: Waiting for Categories button")
                time.sleep(1)

        # Wait until page is loaded and select category from user input
        while True:
            try:
                category_selection_xpath = f"//html/body/form[1]/div[3]/div/fieldset/div[""5]/div[1]/div/div/ul/li[" \
                                           f"@data-option-array-index='{category}']"
                driver.find_element_by_xpath(category_selection_xpath).click()
                break
            except Exception:
                print("[LOG]: Waiting for category dropdown menu")
                time.sleep(1)

        # Wait until page is loaded and click on Consult button
        while True:
            try:
                consult_button_id = "btnConsulta"
                driver.find_element_by_id(consult_button_id).click()
                break
            except Exception:
                print("[LOG]: Waiting for consult button")
                time.sleep(1)

        # Wait html table load the results (grdDocumentos)
        while True:
            try:
                table_html = str(driver.find_element_by_id('grdDocumentos').get_attribute("outerHTML"))
                if ("DFP - Demonstrações Financeiras Padronizadas" in table_html) or \
                    ("ITR - Informações Trimestrais" in table_html):
                    break
            except Exception:
                print("[LOG]: Waiting for results")
                time.sleep(1)

        
        table = LH.fromstring(table_html)
        df = pd.read_html(table_html)[0]

        if self.driver is None: driver.quit()

        return df, table


    def _clean_data(self, cvm_code: int, df_enet_search_result: pd.DataFrame, table: Any) -> pd.DataFrame:
        """
        Perform data cleaning and add link to view or download reports documents

        Parameters
        ----------
        cvm_code : int
            cvm_code
        df_enet_search_result : DataFrame
            ENET Search dataframe result
        table : HTML string with ENET search table result containing links to download and view the reports.

        Returns
        -------
        pandas.Dataframe
            Dataframe containing search cleaned results
        """

        # Cleaning data for CVM code and reference date
        df_enet_search_result["Código CVM"] = cvm_code
        df_enet_search_result['Data Referência'] = df_enet_search_result['Data Referência'].str.split(' ', 1).str[1]
        df_enet_search_result['Data Referência'] = pd.to_datetime(df_enet_search_result["Data Referência"], format="%d/%m/%Y", errors="coerce")

        # Creating a collumn for document visualization link
        link_view = []
        for expression in table.xpath("//tr/td/i[1]/@onclick"):
            link_view.append("https://www.rad.cvm.gov.br/ENET/" + re.findall("(?<=\')(.*?)(?=\')", expression)[0])

        df_enet_search_result["linkView"] = link_view

        # Creating a collumn for document download link
        link_download = []
        for expression in table.xpath("//tr/td/i[2]/@onclick"):
            try:
                data = expression.split(",")
                if "OpenDownloadDocumentos" in data:
                    sequencia, versao, protocolo, tipo = [re.findall("(?<=\')(.*?)(?=\')", d)[0] for d in data]
                    link_download.append(f"https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&"
                                        f"numSequencia={sequencia}&"
                                        f"numVersao={versao}&"
                                        f"numProtocolo={protocolo}&"
                                        f"descTipo={tipo}&"
                                        f"CodigoInstituicao=1")
                else:
                    link_download.append(None)
            except IndexError:
                link_download.append(None)
        df_enet_search_result["linkDownload"] = link_download

        # Filtering for documents which Status is Active
        df_enet_search_result = df_enet_search_result.drop(df_enet_search_result[df_enet_search_result["Status"] != "Ativo"].index)

        # Deleting Actions column
        del df_enet_search_result["Ações"]

        return df_enet_search_result

    def get_cvm_codes(self) -> pd.DataFrame:
        """Returns a dataframe of all CVM codes and Company names

        Returns
        -------
        pandas.Dataframe
            Dataframe of all CVM codes and company names
        """
        if Search.cvm_code_df is not None: return Search.cvm_code_df

        driver = self._instantiate_driver()

        driver.get("https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx")

        # Wait until page is loaded and get all companies data
        while True:
            try:
                companies_result_id = "hdnEmpresas"
                html_data = driver.find_element_by_id(companies_result_id).get_attribute("value")
                if len(html_data) == 0:
                    continue
                break
            except Exception:
                print("[LOG]: Waiting CVM codes")
                time.sleep(1)

        # Selecting company name and CVM code
        list_cod_cvm = re.findall(r"(?<=key:'C_)(.*?)(?=\')", html_data)
        list_nome_emp = re.findall(r"(?<=value:')\d+ - (.*?)(?=\')", html_data)

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
        
        df = self._clean_data(cvm_code, df, table)

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
        
        df = self._clean_data(cvm_code, df, table)

        return df


class SearchFundsData:
    """
    An instance of a Fund can fetch useful information about Brazilian Funds
    """

    def __init__(self,
                 reference_date: datetime):
        self.reference_date = reference_date

    def get_daily_data(self):
        """
        Retrieve funds' daily data such from CVM (quota, pl, capitação, etc.)
        """
        year = self.reference_date.year
        month = str(self.reference_date.month).zfill(2)
        url = f"http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{year}{month}.csv"

        columns = ["CNPJ_FUNDO",
                   "DT_COMPTC",
                   "VL_TOTAL",
                   "VL_QUOTA",
                   "VL_PATRIM_LIQ",
                   "CAPTC_DIA",
                   "RESG_DIA",
                   "NR_COTST"]

        df = pd.DataFrame(columns=columns)

        try:
            df_funds_daily_data = pd.read_csv(url,
                                              sep=";",
                                              encoding="latin",
                                              decimal=".",
                                              header=0)
            df_funds_daily_data = df_funds_daily_data[columns]

        except Exception as exp:
            if 'HTTP Error 404: Not Found' in str(exp):
                print(f"Funds daily data is not available for this date: {self.reference_date}, {url}")
            else:
                raise
        
        # Clean data
        df_funds_daily_data["CNPJ_FUNDO"] = df_funds_daily_data["CNPJ_FUNDO"].str.replace(r'[^0-9]+', '')
        #df_funds_daily_data["CNPJ_FUNDO"] = pd.to_numeric(df_funds_daily_data["CNPJ_FUNDO"], errors="coerce")

        numeric_columns = ["VL_TOTAL",
                           "VL_QUOTA",
                           "VL_PATRIM_LIQ",
                           "CAPTC_DIA",
                           "RESG_DIA",
                           "NR_COTST"]
        
        for column in numeric_columns:
            df_funds_daily_data[column] = pd.to_numeric(df_funds_daily_data[column], errors="coerce")
        
        date_columns = ["DT_COMPTC"]

        for column in date_columns:
            df_funds_daily_data[column] = pd.to_datetime(df_funds_daily_data[column], format="%Y-%m-%d", errors="coerce")
        
        new_columns_names = {}
        for column_name in columns:
            new_columns_names[column_name] = column_name.lower()

        df_funds_daily_data.rename(columns=new_columns_names, inplace=True)

        return df_funds_daily_data
