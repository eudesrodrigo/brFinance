import logging

import pandas as pd
from bs4 import BeautifulSoup
import json

from brfinance.utils import extract_substring
from brfinance.constants import ENET_URL


class GetSearchResponse():
    def __init__(self, response) -> None:
        self.response = response

    def data(self):
        reponse_json = self.response.json()
        return self._parse_get_search(reponse_json)

    def _parse_get_search(self, reponse_json):

        columns = ['cod_cvm', 'empresa', 'categoria', 'tipo', 'especie', 'ref_date', 'data_entrega', 'status', 'version', 'modalidade', "acoes", "outros", 'view_url', 'numero_seq_documento', 'codigo_tipo_instituicao']
        response_df = pd.DataFrame(columns=columns)

        dados = reponse_json["d"]["dados"]

        if dados != "":
            data = dados.replace("<spanOrder>", "").replace("</spanOrder>", "")

            search_results_df = pd.DataFrame([x.split('$&') for x in data.split('$&&*')])
            new_columns_names = ["cod_cvm", "empresa", "categoria", "tipo", "especie", "ref_date", "data_entrega", "status", "version", "modalidade", "acoes"]

            if len(search_results_df.columns) > len(new_columns_names):
                new_columns_names.append("outros")

            search_results_df.columns = new_columns_names

            if (not search_results_df.empty) and ("frmGerenciaPaginaFRE" in dados):
                # Obtem coluna de links
                new = search_results_df["acoes"].str.split("> ", n=-1, expand=True)
                search_results_df["view_url"] = new[0]

                search_results_df.replace("", float("NaN"), inplace=True)
                search_results_df.replace("None", float("NaN"), inplace=True)
                search_results_df.dropna(subset=["cod_cvm"], inplace=True)

                search_results_df['view_url'] = ENET_URL + search_results_df.apply(
                    lambda row: extract_substring(
                        "OpenPopUpVer('", "') ", row['view_url']),  axis=1)

                search_results_df['numero_seq_documento'] = search_results_df.apply(
                    lambda row: extract_substring(
                        "NumeroSequencialDocumento=", "&", row['view_url']), axis=1)

                new = search_results_df['view_url'].str.split("CodigoTipoInstituicao=", n=-1, expand=True)
                search_results_df['codigo_tipo_instituicao'] = new[1]
            response_df = response_df.append(search_results_df)

        response_df['cod_cvm'] = response_df['cod_cvm'].str.replace(r'\D+', '')

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
        hdnEmpresas = BeautifulSoup(html, features="lxml").find(id='hdnEmpresas')
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
        data = self._parse_get_consulta_externa_cvm_categories(self.response.text)
        return data

    def _parse_get_consulta_externa_cvm_categories(self, html):
        hdnComboCategoriaTipoEspecie = BeautifulSoup(html, features="lxml").find(id='hdnComboCategoriaTipoEspecie')
        hdnComboCategoriaTipoEspecie = hdnComboCategoriaTipoEspecie.attrs["value"]

        hdnComboCategoriaTipoEspecie = BeautifulSoup(hdnComboCategoriaTipoEspecie, features="lxml").find_all('option')

        categories = {}

        for option in hdnComboCategoriaTipoEspecie:
            categories[option.attrs["value"]] = option.getText().replace(u'\xa0', u'')

        return categories
