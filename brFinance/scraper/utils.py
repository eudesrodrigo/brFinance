import pandas as pd
import requests
import os
import glob
import re
import urllib.request
from bs4 import BeautifulSoup
from zipfile import ZipFile
from io import BytesIO
from urllib.parse import urljoin
from datetime import datetime, timedelta
from fake_useragent import UserAgent

from brFinance.utils.browser import Browser


def obtemDadosCadastraisCVM(compAtivas=True, codCVM=False):
    """
    Returns a dataframe of Registration data for all Companies available at http://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv
    """
    url = "http://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
    #s = requests.get(url).content
    dados_cadastrais_empresas = pd.read_csv(url, sep=";", encoding="latin")

    if compAtivas:
        dados_cadastrais_empresas = dados_cadastrais_empresas[
            dados_cadastrais_empresas["SIT"] == "ATIVO"]

    if codCVM:
        dados_cadastrais_empresas = dados_cadastrais_empresas[dados_cadastrais_empresas["CD_CVM"] == int(
            codCVM)]

    return dados_cadastrais_empresas


def composicao_capital_social(codCVM):
    """
    This metodh will be deprecated
    """

    dfQuantPapeis = pd.DataFrame()
    for cod in codCVM:
        erro = 1
        cod = str(cod)
        while erro <= 3:
            try:
                print(cod)
                url = "http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/empresas/ExecutaAcaoConsultaInfoEmp.asp?CodCVM={codCVM}".format(
                    codCVM=cod)

                #
                html_content = requests.get(url).content.decode("utf8")

                tableDados = BeautifulSoup(html_content, "lxml").find(
                    "div", attrs={"id": "accordionDados"})
                tickers = re.findall(
                    "'[a-z|A-Z|0-9][a-z|A-Z|0-9][a-z|A-Z|0-9][a-z|A-Z|0-9][0-9][0-9]?'", str(tableDados))
                tickers = [ticker.replace("'", "") for ticker in tickers]
                tickers = list(dict.fromkeys(tickers))

                tickers = pd.DataFrame(tickers, columns=['ticker'])
                tickers["codCVM"] = cod

                dicCapitalSocial = BeautifulSoup(html_content, "lxml").find(
                    "div", attrs={"id": "divComposicaoCapitalSocial"})

                dfs = pd.read_html(str(dicCapitalSocial), thousands='.')[0]

                dfs.columns = ["Tipo", "Quantidade"]

                dfs["codCVM"] = cod
                dfs["dt_load"] = datetime.now()

                dfs = tickers.merge(dfs, on="codCVM")
                print(dfs)
                dfQuantPapeis = dfQuantPapeis.append(dfs)
                break
            except Exception as exp:
                print("Tentando novamente:", cod)
                print(str(exp))
                erro += 1
        print("*"*50)

    return dfQuantPapeis


def obter_dados_negociacao(dateToday=datetime.now().strftime("%Y-%m-%d")):

    print(dateToday)
    url = f"https://arquivos.b3.com.br/api/download/requestname?fileName=InstrumentsConsolidated&date={dateToday}"

    payload = {}
    ua = UserAgent()

    headers = {
        'User-Agent': str(ua.chrome)}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.ok:
        token = response.json().get('token')
        baseURL = f"https://arquivos.b3.com.br/api/download/?token={token}"
        data = pd.read_csv(baseURL,
                           sep=";",
                           encoding='latin-1',
                           error_bad_lines=True)
        data["data_load"] = datetime.now()

        print("Baixando arquivo!")
        r = urllib.request.urlopen(
            "https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetFileDownload/NDY0ODk=").read()

        print("Descompactando arquivo!")
        file = ZipFile(BytesIO(r))
        dfEmissor = file.open("EMISSOR.TXT")

        print("Abrindo arquivo CSV!")
        dfEmissor = pd.read_csv(dfEmissor, header=None, names=[
                                "CODIGO DO EMISSOR", "NOME DO EMISSOR", "CNPJ", "DATA CRIAÇÃO EMISSOR"])

        data = data.merge(dfEmissor, left_on="AsstDesc",
                          right_on="CODIGO DO EMISSOR", how="left")

        data.reset_index(drop=True, inplace=True)

    else:
        data = None

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

def cota_fundos(cnpj):
    columns = ['cota','data','patrimonio','cotistas']
    dfCotas =  pd.DataFrame([],columns=columns)
    try:
        dfCotas = pd.read_json("https://assets-comparacaodefundos.s3-sa-east-1.amazonaws.com/cvm/{cnpj}".format(cnpj=cnpj))
        dfCotas.columns = columns
        dfCotas = dfCotas.set_index(['data'])
    except:
        print('Nenhum fundo encontrado para o CNPJ: {cnpj}'.format(cnpj=cnpj))
    return dfCotas