from time import sleep
from typing import Dict

import pandas as pd
from selenium import webdriver

from brFinance.utils.browser import Browser


class FinancialReport:
    MAX_RETRIES: int = 10

    def __init__(self, link: str, driver: webdriver = None):
        self.link = link
        self.driver = driver

    def _instantiate_driver(self) -> webdriver:
        if self.driver is None:
            driver = Browser.run_chromedriver()
        else:
            driver = self.driver

        return driver

    def _fetch_statement(self, driver, statement):
        driver.find_element_by_xpath(f"//select[@name='cmbQuadro']/option[text()='{statement}']").click()
        iframe = driver.find_element_by_xpath("//iframe[@id='iFrameFormulariosFilho']")
        driver.switch_to.frame(iframe)
        html = driver.page_source

        return html

    def _clean_statement(self, document_version, driver, html, reference_date, statement, statement_dict):

        index_moeda = -1
        if statement == "Demonstração do Fluxo de Caixa":
            index_moeda = -2

        currency_unit = driver.find_element_by_id('TituloTabelaSemBorda').text
        currency_unit = currency_unit.split(" - ")[index_moeda].replace("(", "").replace(")", "")

        table_index = 0
        if statement == "Demonstração das Mutações do Patrimônio Líquido":
            table_index = 1

        df = pd.read_html(html, header=0, decimal=',')[table_index]
        converters = {c: lambda x: str(x) for c in df.columns}
        df = pd.read_html(html, header=0, decimal=',', converters=converters)[table_index]

        for ind, column in enumerate(df.columns):
            if column.strip() != "Conta" and column.strip() != "Descrição":
                df[column] = df[column].astype(str).str.strip().str.replace(".", "")
                df[column] = pd.to_numeric(df[column], errors='coerce')
            else:
                df[column] = df[column].astype(str).str.strip().astype(str)

        # Get first column (most recent data available)
        if statement != "Demonstração das Mutações do Patrimônio Líquido":
            df = df.iloc[:, 0:3]
            df.set_axis([*df.columns[:-1], 'Valor'], axis=1, inplace=True)

        df["refDate"] = reference_date
        df["document_version"] = document_version
        df["currency_unit"] = currency_unit
        df["refDate"] = pd.to_datetime(df["refDate"], errors="coerce")

        statement_dict[statement] = df

    def get_report(self) -> Dict:
        """
        Returns a dictionary with financial reports available

        Returns
        -------
        Dict
            Dictionary with financial reports available
        """
        driver = self._instantiate_driver()
        report_data = {}

        for _ in range(self.MAX_RETRIES):
            print("Coletando dados do link:", self.link)
            try:
                driver.get(self.link)
                options_text = []

                # Wait page load the reports
                for _ in range(self.MAX_RETRIES):
                    # Names for each type of report
                    options_text = [x.get_attribute("text") for x in
                                    driver.find_element_by_name("cmbQuadro").find_elements_by_tag_name("option")]
                    if len(options_text) > 0: break
                    sleep(1)

                # Navigate through reports and save each dataframe in a dictionary
                reference_date = driver.find_element_by_id('lblDataDocumento').text
                document_version = driver.find_element_by_id('lblDescricaoCategoria').text.split(" - ")[-1].replace("V",
                                                                                                                    "")
                cvm_code = driver.find_element_by_id('hdnCodigoCvm').get_attribute("value")

                report_data["reference_date"] = reference_date
                report_data["version"] = int(document_version)
                report_data["cvm_code"] = int(cvm_code)

                statement_dict = {}
                for statement in options_text:
                    print(statement)

                    html = self._fetch_statement(driver, statement)
                    self._clean_statement(document_version, driver, html, reference_date, statement, statement_dict)

                    driver.switch_to.default_content()

                print("-" * 60)
                report_data["reports"] = statement_dict
                break
            except Exception as exp:
                print("Erro ao carregar demonstrativo. Tentando novamente...")
                print(exp)

        if self.driver is None: driver.quit()

        return report_data
