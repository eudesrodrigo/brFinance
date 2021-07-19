import re
import pandas as pd
import lxml.html as LH
from time import sleep
from datetime import datetime
from selenium import webdriver
from dataclasses import dataclass

from brFinance.utils.browser import Browser


@dataclass
class SearchENET:
    """
    Perform webscraping on the page https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx according to the input parameters
    """

    def __init__(self, cod_cvm: int = None, category: int = None, driver: webdriver = None):
        self.driver = driver
        
        # self.cod_cvm_dataframe = self.cod_cvm_list()
        
        self.cod_cvm = cod_cvm
        if cod_cvm is not None:
            self.check_cod_cvm_exist(self.cod_cvm)
        
        self.category = category
        if category is not None:
            self.check_category_exist(self.category)


    def cod_cvm_list(self) -> pd.DataFrame:
        """
        Returns a dataframe of all CVM codes and Company names availble at https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx
        """

        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver=self.driver

        driver.get("https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx")

        #wait_pageload()
        for retrie in range(50):
            try:
                html = str(driver.find_element_by_id('hdnEmpresas').get_attribute("value"))
                listCodCVM = re.findall(r"(?<=\_)(.*?)(?=\')", html)
                listNomeEmp = re.findall(r"(?<=\-)(.*?)(?=\')", html)
                codigos_cvm = pd.DataFrame(list(zip(listCodCVM, listNomeEmp)),
                                columns=['codCVM', 'nome_empresa'])
                codigos_cvm['codCVM'] = pd.to_numeric(codigos_cvm['codCVM'])
                if len(codigos_cvm.index) > 0:
                    break
                else:
                    sleep(1)
            except:
                sleep(1)

        if self.driver is None:
            driver.quit()

        return codigos_cvm
    

    def check_cod_cvm_exist(self, cod_cvm) -> bool:
        codigos_cvm_available = self.cod_cvm_list()
        cod_cvm_exists = str(cod_cvm) in [str(cod_cvm_aux) for cod_cvm_aux in codigos_cvm_available['codCVM'].values]
        if cod_cvm_exists:
            return True
        else:
            raise ValueError('Código CVM informado não encontrado.')
            

    def check_category_exist(self, category) -> bool:
        search_categories_list = [21, 39]
        if category in search_categories_list:
            return True
        else:
            raise ValueError('Invalid category value. Available categories are:', search_categories_list)


    @property
    def search(self) -> pd.DataFrame:
        """
        Returns dataframe of search results including cod_cvm, report's url, etc.
        """

        dataInicial = '01012010'
        dataFinal = datetime.today().strftime('%d%m%Y')
        option_text = str(self.category)
        
        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver=self.driver
        
        driver.get(f"https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx?codigoCVM={str(self.cod_cvm)}")

        # Wait and click cboCategorias_chosen
        for errors in range(10):
            try:
                driver.find_element_by_id('cboCategorias_chosen').click()
                break
            except:
                sleep(1)

        # Wait and click
        for errors in range(10):
            try:
                driver.find_element_by_xpath(
                    f"//html/body/form[1]/div[3]/div/fieldset/div[5]/div[1]/div/div/ul/li[@data-option-array-index='{option_text}']").click()
                break
            except:
                sleep(1)

        # Wait and click
        for errors in range(10):
            try:
                driver.find_element_by_xpath("//html/body/form[1]/div[3]/div/fieldset/div[4]/div[1]/label[4]").click()
                break
            except:
                sleep(1)
        
        # Wait and send keys txtDataIni
        for errors in range(10):
            try:
                driver.find_element_by_id('txtDataIni').send_keys(dataInicial)
                break
            except:
                sleep(1)

        # Wait and send keys txtDataFim
        for errors in range(10):
            try:
                driver.find_element_by_id('txtDataFim').send_keys(dataFinal)
                break
            except:
                sleep(1)
        
        # Wait and click btnConsulta
        for errors in range(10):
            try:
                driver.find_element_by_id('btnConsulta').click()
                break
            except:
                sleep(1)

        # Wait html table load the results (grdDocumentos)
        for errors in range(10):
            try:
                table_html = pd.read_html(str(driver.find_element_by_id('grdDocumentos').get_attribute("outerHTML")))[-1]
                if len(table_html.index) > 0:
                    break
                else:
                    sleep(1)
            except:
                sleep(1)

        table_html = str(driver.find_element_by_id('grdDocumentos').get_attribute("outerHTML"))
        table = LH.fromstring(table_html)
        results = pd.read_html(table_html)

        for df_result in results:
            if len(df_result.index) > 0:
                pattern = "OpenPopUpVer(\'(.*?)\')"
                df_result['linkView'] = table.xpath('//tr/td/i[1]/@onclick')
                df_result['linkDownload'] = table.xpath('//tr/td/i[2]/@onclick')

                df_result['linkView'] = "https://www.rad.cvm.gov.br/ENET/" + \
                    df_result['linkView'].str.extract(r"(?<=\')(.*?)(?=\')", expand=False)

                df3 = df_result['linkDownload'].str.split(',', expand=True)
                df3.columns = ['COD{}'.format(x+1) for x in df3.columns]
                df_result = df_result.join(df3)
                df_result['linkDownload'] = "https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&numSequencia=" + \
                    df_result['COD1'].str.extract(r"(?<=\')(.*?)(?=\')", expand=False) + \
                    "&numVersao=" + df_result['COD2'].str.extract(r"(?<=\')(.*?)(?=\')", expand=False) + \
                    "&numProtocolo=" + df_result['COD3'].str.extract(r"(?<=\')(.*?)(?=\')", expand=False) + \
                    "&descTipo=" + df_result['COD4'].str.extract(r"(?<=\')(.*?)(?=\')", expand=False) + \
                    "&CodigoInstituicao=1"

                df_result = df_result[['Código CVM', 'Empresa', 'Categoria', 'Tipo', 'Espécie',
                                'Data Referência', 'Data Entrega', 'Status', 'V', 'Modalidade',
                                    'linkView', 'linkDownload']]

                df_result['Data Referência'] = df_result['Data Referência'].str.split(
                    ' ', 1).str[1]

                df_result['Data Referência'] = pd.to_datetime(
                    df_result["Data Referência"], format="%d/%m/%Y", errors="coerce")

                df_result = df_result[df_result["Status"] == "Ativo"]
                df_result["Código CVM"] = self.cod_cvm
                df_result = df_result[['Código CVM', 'Empresa', 'Categoria', 'Tipo', 'Espécie',
                                'Data Referência', 'Data Entrega', 'Status', 'V', 'Modalidade',
                                    'linkView', 'linkDownload']]

            df_result = df_result.reset_index(drop=True)
            break

        if self.driver is None:
            driver.quit()

        print(f"Resultados da busca ENET: {len(df_result.index)}")
        return df_result
