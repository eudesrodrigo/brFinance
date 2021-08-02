import glob
import os
import urllib.request
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from zipfile import ZipFile
import time

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
    archive = ZipFile( isin_file_path, 'r')
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


def obter_indices_anbima(dataIni, dataFim):
    link = "https://www.anbima.com.br/informacoes/ima/ima-sh.asp"
    driver = Browser.run_chromedriver()
    #dataIni = datetime.now().strftime("%d%m%Y")
    dataIni = datetime.strptime(dataIni, '%d/%m/%Y')
    dataFim = datetime.strptime(dataFim, '%d/%m/%Y')
    root = os.getcwd() + "/downloads"
    try:
        os.makedirs(root)
    except FileExistsError:
        # directory already exists
        pass

    # Remover arquivos da pasta de destino do download antes de iniciar novo scrapping
    files = glob.glob(root)
    f = []
    for (dirpath, dirnames, filenames) in os.walk(root):
        for file in filenames:
            if file.endswith(".csv"):
                os.remove(root + "/" + file)

    while dataFim >= dataIni:
        try:
            dateAux = dataFim.strftime("%d%m%Y")
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
            dataFim -= timedelta(days=1)
        except Exception as excep:
            print(str(excep))

    f = []
    dfAmbima = pd.DataFrame()
    for (dirpath, dirnames, filenames) in os.walk(root):
        for file in filenames:
            try:
                df = pd.read_csv(root + "/" + file, header=1,
                                 sep=";", encoding="latin", thousands=".")
                os.remove(root + "/" + file)
                dfAmbima = dfAmbima.append(df)
            except:
                continue

    # Tipos de dados
    dfAmbima = dfAmbima.replace("--", "")
    dfAmbima["Data de Referência"] = pd.to_datetime(
        dfAmbima["Data de Referência"], format='%d/%m/%Y', errors='coerce')
    for column in dfAmbima.columns:
        if column != "Data de Referência" and column != "Índice":
            print(column)
            dfAmbima[column] = dfAmbima[column].astype(
                str).str.replace('.', '')
            dfAmbima[column] = dfAmbima[column].astype(
                str).str.replace(',', '.')
            dfAmbima[column] = pd.to_numeric(dfAmbima[column])
    driver.quit()

    return dfAmbima.reset_index(drop=True)


def obter_cotacao_moeda(startDate, endDate, codMoeda="61"):
    urlDolar = f'https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda={codMoeda}&DATAINI={startDate}&DATAFIM={endDate}'
    columnNames = ["Date", "Tipo", "Moeda", "Compra", "Venda"]
    dfMoeda = pd.read_csv(urlDolar,
                          sep=";",
                          encoding="latin",
                          decimal=",",
                          index_col=0,
                          names=columnNames,
                          usecols=[0, 2, 3, 4, 5]
                          )

    dfMoeda.index = pd.to_datetime(
        [str(x).zfill(8) for x in dfMoeda.index], format="%d%m%Y", errors='coerce')

    dfMoeda["Compra"] = pd.to_numeric(
        dfMoeda["Compra"].astype(str).str.replace(',', '.'))
    dfMoeda["Venda"] = pd.to_numeric(
        dfMoeda["Venda"].astype(str).str.replace(',', '.'))

    return dfMoeda.sort_index()
