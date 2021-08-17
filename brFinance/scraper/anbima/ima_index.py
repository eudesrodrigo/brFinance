from brFinance.utils.browser import Browser, DOWNLOAD_PATH
import pandas as pd
from datetime import datetime, timedelta
import os
import time


class AnbimaMarketIndex:
    """
    IMA Index from ANBIMA
    """

    def __init__(self, date_begin: datetime, date_end: datetime = datetime.now()):
        """
        Parameters
        ----------
        date_begin : datetime
            Start date
        date_end : datetime
            End date
        """
        self.date_begin = date_begin
        self.date_end = date_end
        

    def get_ima(self, delete_downloaded_files: bool = True) -> pd.DataFrame:
        """
        Get IMA (ANBIMA MARKET INDEX) historic data for a period of time
        """

        link = "https://www.anbima.com.br/informacoes/ima/ima-sh.asp"
        driver = Browser.run_chromedriver()

        dfAmbima = pd.DataFrame()
        while self.date_end >= self.date_begin:
            dateAux = self.date_end.strftime("%d%m%Y")
            file_name = f"{DOWNLOAD_PATH}/IMA_SH_{dateAux}.csv"
            
            if not os.path.exists(file_name):
                
                driver.get(link)
                driver.find_element_by_xpath(
                    "//input[@name='escolha'][@value='2']").click()
                driver.find_element_by_xpath(
                    "//input[@name='saida'][@value='csv']").click()
                dateInput = driver.find_element_by_xpath("//input[@name='Dt_Ref']")
                dateInput.click()
                dateInput.clear()
                dateInput.send_keys(dateAux)
                driver.find_element_by_xpath("//img[@name='Consultar']").click()
                
            Browser.download_wait()

            while not os.path.isfile(file_name):
                time.sleep(1)

            try:
                df = pd.read_csv(file_name, header=1, sep=";", encoding="latin", thousands=".")
                dfAmbima = dfAmbima.append(df)
            except:
                pass

            if delete_downloaded_files:
                os.remove(file_name)
            self.date_end -= timedelta(days=1)

        # Clear dataframe
        dfAmbima = dfAmbima.replace("--", "")
        dfAmbima["Data de Referência"] = pd.to_datetime(
            dfAmbima["Data de Referência"], format='%d/%m/%Y', errors='coerce')
        for column in dfAmbima.columns:
            if column != "Data de Referência" and column != "Índice":
                dfAmbima[column] = dfAmbima[column].astype(
                    str).str.replace('.', '')
                dfAmbima[column] = dfAmbima[column].astype(
                    str).str.replace(',', '.')
                dfAmbima[column] = pd.to_numeric(dfAmbima[column])
        print(dfAmbima.columns)
        
        dfAmbima = dfAmbima[['Índice',
                            'Data de Referência',
                            "Número Índice",
                            "Peso(%)",
                            "Duration(d.u.)",
                            "Carteira a Mercado (R$ mil)",
                            "Número de<BR>Operações *",
                            "Quant. Negociada (1.000 títulos) *",
                            "Valor Negociado (R$ mil) *",
                            "PMR",
                            "Convexidade",
                            "Yield",
                            "Redemption Yield"]]

        new_columns_names = {'Índice': 'indice',
                            'Data de Referência': 'reference_date',
                            "Número Índice": "numero_indice",
                            "Peso(%)": "peso_percentual",
                            "Duration(d.u.)": "duration",
                            "Carteira a Mercado (R$ mil)": "carteira_a_mercado",
                            "Número de<BR>Operações *": "numero_operacoes",
                            "Quant. Negociada (1.000 títulos) *": "quant_negociada",
                            "Valor Negociado (R$ mil) *": "valor_negociado",
                            "PMR": "pmr",
                            "Convexidade": "convexidade",
                            "Yield": "yield",
                            "Redemption Yield": "redemption_yield"}

        dfAmbima.rename(columns=new_columns_names, inplace=True)
        
        driver.quit()

        return dfAmbima.reset_index(drop=True)

