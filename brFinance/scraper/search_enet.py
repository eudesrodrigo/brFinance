import re
import pandas as pd
import lxml.html as LH

from brFinance.utils.browser import Browser
from dataclasses import dataclass
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
    DELAY = 20

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

    def cod_cvm_list(self) -> pd.DataFrame:
        """Returns a dataframe of all CVM codes and Company names

        Returns
        -------
        pandas.Dataframe
            Dataframe of all CVM codes and company names
        """

        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver = self.driver

        driver.get("https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx")

        # Wait until page is loaded and get all companies data
        companies_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.ID, 'hdnEmpresas'))
        )

        # Selecting company name and CVM code
        html_data = companies_element.get_attribute("value")
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

        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver = self.driver

        data_inicial = '01012010'
        data_final = datetime.today().strftime('%d%m%Y')
        option_text = str(self.category)

        driver.get(f"https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx?codigoCVM={str(self.cod_cvm)}")

        # Wait until page is loaded and click Categories button
        category_button_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.ID, 'cboCategorias_chosen'))
        )
        ActionChains(driver).move_to_element(category_button_element).click().perform()

        # Wait until page is loaded and select category from user input
        category_type_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.XPATH, f"//html/body/form[1]/div[3]/div/fieldset/div[5]/div["
                                                      f"1]/div/div/ul/li[@data-option-array-index='{option_text}']"))
        )
        ActionChains(driver).move_to_element(category_type_element).click().perform()

        # Wait until page is loaded and click Period button
        period_type_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.XPATH, "//html/body/form[1]/div[3]/div/fieldset/div[4]/div[1]/label[4]"))
        )
        ActionChains(driver).move_to_element(period_type_element).click().perform()

        # Wait until page is loaded and send keys for initial date
        period_init_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.ID, 'txtDataIni'))
        )
        ActionChains(driver).move_to_element(period_init_element).send_keys(data_inicial).perform()

        # Wait until page is loaded and send keys for end date
        period_end_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.ID, 'txtDataFim'))
        )
        ActionChains(driver).move_to_element(period_end_element).send_keys(data_final).perform()

        # Wait until page is loaded and click on Consult button
        consult_element = WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.ID, 'btnConsulta'))
        )
        ActionChains(driver).move_to_element(consult_element).click().perform()

        # Wait html table load the results (grdDocumentos)
        WebDriverWait(driver, SearchENET.DELAY).until(
            EC.presence_of_element_located((By.XPATH, '//table[@id="grdDocumentos"]/tbody//tr'))
        )
        table_html = str(driver.find_element_by_id('grdDocumentos').get_attribute("outerHTML"))
        table = LH.fromstring(table_html)
        df = pd.read_html(table_html)[0]

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

        if self.driver is None:
            driver.quit()

        return df
