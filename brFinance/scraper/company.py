import re
import os
import pickle
import pandas as pd
from dataclasses import dataclass
from typing import List, Text, Dict

from brFinance.utils.browser import Browser
from brFinance.utils.file import File
from brFinance.scraper.financial_report import FinancialReport
from brFinance.scraper.search_enet import SearchENET
from brFinance.scraper.utils import composicao_capital_social, obtemDadosCadastraisCVM


@dataclass
class Company:
    def __init__(self, cod_cvm: int):
        self.cod_cvm = cod_cvm


    def obtemCompCapitalSocial(self):
        self.ComposicaoCapitalSocial = composicao_capital_social(self.cod_cvm)


    def obterDadosCadastrais(self):
        listaCodCVM = obtemDadosCadastraisCVM(self.cod_cvm)
        listaCodCVM = listaCodCVM[listaCodCVM["CD_CVM"] == self.cod_cvm]
        self.dadosCadastrais = listaCodCVM.to_dict('r')


    @property
    def reports(self) -> List:
        driver = Browser.run_chromedriver()
        search_anual_reports = SearchENET(cod_cvm=self.cod_cvm, category=21, driver=driver).search
        search_quarter_reports = SearchENET(cod_cvm=self.cod_cvm, category=39, driver=driver).search
        search_reports_result = search_anual_reports.append(search_quarter_reports)

        reports = {}
        for index, report_info in search_reports_result.iterrows():
            
            m = re.search(r"(?<=\Documento=)(.*?)(?=\&)", report_info['linkView'])
            if m:
                document_number = m.group(1)
            
            # Create folder and save reports locally
            path_save_reports = f'{os.getcwd()}/reports'
            report_file = f'{path_save_reports}/{document_number}.plk'
            File.create_folder(path_save_reports)

            # Check if report is available locally, otherwise scrape it.
            if File.check_exist(report_file):
                with open(report_file, 'rb') as load_report:
                    report_obj = pickle.load(load_report)
                    print("Carregado localmente!")
            else:
                report_obj = FinancialReport(link=report_info["linkView"], driver=driver).financial_reports
                with open(report_file, 'wb') as save_report:
                    pickle.dump(report_obj, save_report)

            reports[report_obj["ref_date"]] = report_obj["reports"]
        
        driver.quit()

        return reports