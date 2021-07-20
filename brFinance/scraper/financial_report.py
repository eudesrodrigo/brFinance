import pandas as pd
from time import sleep
from selenium import webdriver
from dataclasses import dataclass
from typing import List, Text, Dict

from brFinance.utils.browser import Browser


@dataclass
class FinancialReport:
    def __init__(self, link: str, driver: webdriver = None):
        self.link = link
        self.driver = driver

    @property
    def financial_reports(self) -> Dict:
        """
        Returns a dictionary with financial reports available in a page such as 
        Reports currently available:
        - 
        """
        link = self.link

        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver=self.driver

        erros = 0
        max_retries = 10
        
        dictDemonstrativos = None

        while erros < max_retries:
            try:
                print("Coletando dados do link:", link)
                driver.get(link)

                # Wait page load the reports
                for retrie in range(max_retries):
                    # Quando o captcha é que quebrado, options_text trás as opções de demonstrativos
                    options_text = [x.get_attribute("text") for x in driver.find_element_by_name(
                        "cmbQuadro").find_elements_by_tag_name("option")]

                    if len(options_text) > 0:
                        break
                    else:
                        sleep(1)

                # Navega nos demonstrativos e salva o dataframe no dicionario
                refDate = driver.find_element_by_id('lblDataDocumento').text
                versaoDoc = driver.find_element_by_id(
                    'lblDescricaoCategoria').text.split(" - ")[-1].replace("V", "")
                
                report = {"ref_date": refDate,
                          "versao": int(versaoDoc),
                          "cod_cvm": int(driver.find_element_by_id('hdnCodigoCvm').get_attribute("value"))
                          }

                dictDemonstrativos = {}
                for demonstrativo in options_text:
                    print(demonstrativo)

                    driver.find_element_by_xpath("//select[@name='cmbQuadro']/option[text()='{option_text}']".format(option_text=demonstrativo)).click()

                    iframe = driver.find_element_by_xpath(
                        "//iframe[@id='iFrameFormulariosFilho']")
                    driver.switch_to.frame(iframe)
                    html = driver.page_source

                    if demonstrativo == "Demonstração do Fluxo de Caixa":
                        index_moeda = -2
                    else:
                        index_moeda = -1

                    moedaUnidade = driver.find_element_by_id(
                        'TituloTabelaSemBorda').text.split(" - ")[index_moeda].replace("(", "").replace(")", "")

                    if demonstrativo == "Demonstração das Mutações do Patrimônio Líquido":
                        df = pd.read_html(html, header=0, decimal=',')[1]
                        converters = {c: lambda x: str(x) for c in df.columns}
                        df = pd.read_html(html, header=0, decimal=',',
                                        converters=converters)[1]

                    else:
                        df = pd.read_html(html, header=0, decimal=',')[0]
                        converters = {c: lambda x: str(x) for c in df.columns}
                        df = pd.read_html(html, header=0, decimal=',',
                                        converters=converters)[0]

                    for ind, column in enumerate(df.columns):
                        if column.strip() != "Conta" and column.strip() != "Descrição":
                            df[column] = df[column].astype(
                                str).str.strip().str.replace(".", "")
                            df[column] = pd.to_numeric(df[column], errors='coerce')
                        else:
                            df[column] = df[column].astype(
                                'str').str.strip().astype('str')

                    # Pega apenas a primeira coluna de valores, correspondente ao demonstrativo mais atual, e renomeia para "Valor"
                    if demonstrativo != "Demonstração das Mutações do Patrimônio Líquido":
                        df = df.iloc[:, 0:3]
                        df.set_axis([*df.columns[:-1], 'Valor'],
                                    axis=1, inplace=True)

                    # Add data de referencia e versão aos Dataframes
                    df["refDate"] = refDate
                    df["versaoDoc"] = versaoDoc
                    df["moedaUnidade"] = moedaUnidade

                    df["refDate"] = pd.to_datetime(df["refDate"], errors="coerce")

                    # Add ao dicionario de demonstrativos
                    dictDemonstrativos[demonstrativo] = df

                    driver.switch_to.default_content()

                print("-"*60)

                # Add data de referencia ao ditc de demonstrativos
                report["reports"] = dictDemonstrativos
                break
            except Exception as exp:
                print("Erro ao carregar demonstrativo. Tentando novamente...")
                print(str(exp))
                erros += 1
                continue
        
        if self.driver is None:
            driver.quit()

        return report
