import os
import time
from datetime import datetime
from zipfile import ZipFile

import pandas as pd
import requests
from fake_useragent import UserAgent

from brFinance.utils.browser import Browser, DOWNLOAD_PATH


def obter_dados_negociacao(date=datetime.now().strftime("%Y-%m-%d")):
    print(date)
    # Dados negociacao
    url = f"https://arquivos.b3.com.br/api/download/requestname?fileName=InstrumentsConsolidated&date={date}"

    payload = {}
    ua = UserAgent()

    headers = {
        'User-Agent': str(ua.chrome)}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.ok:
        token = response.json().get('token')
        baseURL = f"https://arquivos.b3.com.br/api/download/?token={token}"
        print(baseURL)
        data = pd.read_csv(baseURL,
                           sep=";",
                           encoding='latin-1',
                           error_bad_lines=True)
        data["data_load"] = datetime.now()
        print(data)

    # ISIN
    driver = Browser.run_chromedriver()
    driver.get(f"https://sistemaswebb3-listados.b3.com.br/isinPage/?language=pt-br")
    driver.find_element_by_xpath("//*[text()='Download de arquivos']").click()
    # Wait until page is loaded and click Period button
    while True:
        try:
            driver.find_element_by_xpath("//*[text()='Banco de Dados Completo']").click()
            break
        except Exception:
            print("[LOG]: Waiting for period button")
            time.sleep(1)

    isin_file_path = DOWNLOAD_PATH + "/isinp.zip"
    if os.path.isfile(isin_file_path):
        os.remove(isin_file_path)
    while not os.path.exists(isin_file_path):
        time.sleep(1)

    Browser.download_wait()
    archive = ZipFile(isin_file_path, 'r')
    if os.path.isfile(isin_file_path):
        os.remove(isin_file_path)
    driver.quit()
    # read file

    dfEmissor = archive.open("EMISSOR.TXT")
    dfEmissor = pd.read_csv(dfEmissor, header=None, names=[
        "CODIGO DO EMISSOR", "NOME DO EMISSOR", "CNPJ", "DATA CRIAÇÃO EMISSOR"])

    data = data.merge(dfEmissor, left_on="AsstDesc",
                      right_on="CODIGO DO EMISSOR", how="left")

    data.reset_index(drop=True, inplace=True)

    #     print("Baixando arquivo!")
    #     r = urllib.request.urlopen(
    #         "https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetFileDownload/NDY0ODk=").read()
    #     file_name = "isin_csv.zip"
    #     open(file_name, 'wb').write(r)

    #     print("Descompactando arquivo!")
    #     r = requests.get("https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetFileDownload/NDY0ODk=", verify=False, stream=True)

    #     open(file_name, 'wb').write(r.content)
    #     archive = ZipFile(file_name, 'r')
    #     dfEmissor = archive.open("EMISSOR.TXT")

    #     print("Abrindo arquivo CSV!")
    #     dfEmissor = pd.read_csv(dfEmissor, header=None, names=[
    #                             "CODIGO DO EMISSOR", "NOME DO EMISSOR", "CNPJ", "DATA CRIAÇÃO EMISSOR"])

    #     data = data.merge(dfEmissor, left_on="AsstDesc",
    #                       right_on="CODIGO DO EMISSOR", how="left")

    #     data.reset_index(drop=True, inplace=True)

    # else:
    #     data = None

    return data


def obtemCodCVM():
    url = "https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/ResultBuscaParticCiaAb.aspx?CNPJNome=&TipoConsult=C"
    print(url)
    tableDados = pd.read_html(url, header=0)[0]
    tableDados = tableDados[~tableDados['SITUAÇÃO REGISTRO'].str.contains(
        "Cancelado")]
    tableDados["CÓDIGO CVM"] = pd.to_numeric(
        tableDados["CÓDIGO CVM"], errors="coerce")
    tableDados = tableDados.drop_duplicates()
    tableDados = tableDados.reset_index(drop=True)

    return tableDados
