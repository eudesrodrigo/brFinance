import logging

import pandas as pd
from bs4 import BeautifulSoup
import json
import io
import zipfile

from brfinance.utils import extract_substring
from brfinance.constants import ENET_URL


class GetSearchResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        reponse_json = self.response.json()
        return self._parse_get_search(reponse_json)

    def _parse_get_search(self, reponse_json):

        columns = ['cod_cvm', 'empresa', 'categoria', 'tipo', 'especie', 'ref_date',
                   'data_entrega', 'status', 'version', 'modalidade', "acoes", "outros"]
        addtional_columns = ['view_url',
                             'numero_seq_documento', 'codigo_tipo_instituicao']

        download_columns = ["numSequencia",
                            "numVersao", "numProtocolo", "descTipo"]

        response_df = pd.DataFrame(
            columns=columns+addtional_columns+download_columns)

        dados = reponse_json["d"]["dados"]

        if dados:
            data = dados.replace("<spanOrder>", "")

            search_results_df = pd.DataFrame(
                [x.split('$&') for x in data.split('$&&*')], columns=columns).iloc[:, :11]

            search_results_df = search_results_df[pd.notnull(
                search_results_df['acoes'])]

            if not search_results_df.empty:
                # Obtem coluna de links
                search_results_df.loc[
                    search_results_df['acoes'].str.contains("OpenPopUpVer\('"),
                    'view_url'] = ENET_URL + search_results_df['acoes'].str.extract('OpenPopUpVer\(\'(.*?)\'\)', expand=False)

                search_results_df[download_columns] = search_results_df['acoes'].str.extract(
                    'OpenDownloadDocumentos\(\'(.*?)\'\)', expand=False).str.replace("'", "", regex=True).str.split(",", expand=True)

                search_results_df.loc[
                    search_results_df['acoes'].str.contains("OpenPopUpVer\('"),
                    'numero_seq_documento'] = search_results_df['acoes'].str.extract('NumeroSequencialDocumento\=(.*?)\&', expand=False)

                search_results_df.loc[
                    search_results_df['acoes'].str.contains("OpenPopUpVer\('"),
                    'codigo_tipo_instituicao'] = search_results_df['acoes'].str.extract("CodigoTipoInstituicao\=(.*?)\'\)", expand=False)

                new = search_results_df['data_entrega'].str.split(
                    "</spanOrder>", n=-1, expand=True)
                search_results_df['data_entrega'] = pd.to_datetime(
                    new[1].str.strip(), format="%d/%m/%Y %H:%M")

                new = search_results_df['ref_date'].str.split(
                    "</spanOrder>", n=-1, expand=True)
                search_results_df['ref_date'] = pd.to_datetime(
                    new[0].str.strip(), format="%Y%m%d")

                search_results_df['cod_cvm'] = search_results_df['cod_cvm'].str.replace(
                    r'\D+', '', regex=True)

                search_results_df = search_results_df.replace(
                    {'</spanOrder>': ''}, regex=True).sort_values('data_entrega', ascending=False)

                response_df = response_df.append(search_results_df)

        return response_df


class GetReportResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = {}
        for key in self.response.keys():
            html = self.response[key]
            data[key] = self._parse_get_reports(html.text, key)

        return data

    def _parse_get_reports(self, html, report):
        soup = BeautifulSoup(html, features="lxml")
        currency_unit = soup.find(id='TituloTabelaSemBorda').getText()

        index_moeda = -1
        statement = report
        if statement == "Demonstração do Fluxo de Caixa":
            index_moeda = -2

        currency_unit = currency_unit.split(
            " - ")[index_moeda].replace("(", "").replace(")", "")

        table_index = 0
        if statement == "Demonstração das Mutações do Patrimônio Líquido":
            table_index = 1

        df = pd.read_html(html, header=0, decimal=',')[table_index]
        converters = {c: lambda x: str(x) for c in df.columns}
        df = pd.read_html(html, header=0, decimal=',',
                          converters=converters)[table_index]

        for ind, column in enumerate(df.columns):
            if column.strip() != "Conta" and column.strip() != "Descrição":
                df[column] = df[column].astype(
                    str).str.strip().str.replace(".", "", regex=True)
                df[column] = pd.to_numeric(df[column], errors='coerce')
            else:
                df[column] = df[column].astype(str).str.strip().astype(str)

        # Get first column (most recent data available)
        if statement != "Demonstração das Mutações do Patrimônio Líquido":
            df = df.iloc[:, 0:3]
            df.set_axis([*df.columns[:-1], 'Valor'], axis=1, inplace=True)

        # df["refDate"] = reference_date
        #df["refDate"] = pd.to_datetime(df["refDate"], errors="coerce")
        # df["document_version"] = document_version
        df["currency_unit"] = currency_unit

        return df


class GetCVMCodesResponse():

    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_cvm_codes(self.response.text)
        return data

    def _parse_get_cvm_codes(self, html):
        hdnEmpresas = BeautifulSoup(
            html, features="lxml").find(id='hdnEmpresas')
        hdnEmpresas = hdnEmpresas.attrs["value"]
        hdnEmpresas = hdnEmpresas.replace('{ key:', '{ "key":')
        hdnEmpresas = hdnEmpresas.replace(', value:', ', "value":')
        hdnEmpresas = hdnEmpresas.replace("'", '"')
        empresas_json = json.loads(hdnEmpresas)

        empresas = {}
        for empresa in empresas_json:
            empresa_value = empresa["value"].split(" - ")
            empresas[empresa_value[0]] = empresa_value[-1]
        return empresas


class GetCategoriesResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_consulta_externa_cvm_categories(
            self.response.text)
        return data

    def _parse_get_consulta_externa_cvm_categories(self, html):
        hdnComboCategoriaTipoEspecie = BeautifulSoup(
            html, features="lxml").find(id='hdnComboCategoriaTipoEspecie')
        hdnComboCategoriaTipoEspecie = hdnComboCategoriaTipoEspecie.attrs["value"]

        hdnComboCategoriaTipoEspecie = BeautifulSoup(
            hdnComboCategoriaTipoEspecie, features="lxml").find_all('option')

        categories = {}

        for option in hdnComboCategoriaTipoEspecie:
            categories[option.attrs["value"]
                       ] = option.getText().replace(u'\xa0', u'')

        return categories


class GetTipoParticipanteResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_consulta_externa_cvm_tipo_participante(
            self.response.text)
        return data

    def _parse_get_consulta_externa_cvm_tipo_participante(self, html):
        cboTipoParticipante = BeautifulSoup(
            html, features="lxml").find(id='cboTipoParticipante')

        cboTipoParticipante = cboTipoParticipante.find_all('option')

        tipo_participante = {}

        for option in cboTipoParticipante:
            tipo_participante[option.attrs["value"]
                              ] = option.getText()

        return tipo_participante


class GetCadastroInstrumentosTokenResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_cadastro_instrumentos_token(
            self.response.json())
        return data

    def _parse_get_cadastro_instrumentos_token(self, json_response):
        return json_response["token"]


class GetCadastroInstrumentosResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_cadastro_instrumentos(self.response.text)
        return data

    def _parse_get_cadastro_instrumentos(self, csv):
        ativos = pd.read_csv(io.StringIO(csv), sep=";")

        return ativos


class GetEmissorResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_emissor(self.response.content)
        return data

    def _parse_get_emissor(self, content):
        file = zipfile.ZipFile(io.BytesIO(content))
        emissor_file = file.open('EMISSOR.TXT')

        header = [
            'Asst',
            'descricao',
            'cnpj',
            'outro'
        ]

        emissor_file = pd.read_csv(emissor_file, names=header)
        emissor_file['cnpj'] = pd.to_numeric(emissor_file['cnpj'])

        return emissor_file


class GetPesquisaCiaAbertaResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        data = self._parse_get_pesquisa_cia_aberta(self.response.text)
        return data

    def _parse_get_pesquisa_cia_aberta(self, content):
        cod_cvm_dataframe = pd.read_html(content, header=0)[0]
        cod_cvm_dataframe['CNPJ'] = pd.to_numeric(
            cod_cvm_dataframe['CNPJ'].str.replace(r'\D+', '', regex=True))
        cod_cvm_dataframe.rename(columns={
            'NOME': 'nome',
            'CNPJ': 'cnpj',
            'CÓDIGO CVM': 'cod_cvm',
            'TIPO DE PARTICIPANTE': 'tipo_participante',
            'SITUAÇÃO REGISTRO': 'situacao_registro'}, inplace=True)

        return cod_cvm_dataframe
