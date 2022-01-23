import logging

from bs4 import BeautifulSoup
from datetime import date

from brfinance.connector import CVMHttpClientConnector
from brfinance.constants import BOOL_STRING_MAPPER, ENET_URL
from brfinance.utils import extract_substring

logger = logging.getLogger(__name__)


class CVMHttpClient():
    ENETCONSULTA_URL = "https://www.rad.cvm.gov.br/ENETCONSULTA/"
    LISTAR_DOCUMENTOS_URL = f"{ENET_URL}frmConsultaExternaCVM.aspx/ListarDocumentos"
    ENET_CONSULTA_EXTERNA = f"{ENET_URL}frmConsultaExternaCVM.aspx"

    def __init__(
            self,
            session: CVMHttpClientConnector):

        self.session = session

    def get_search_results(
            self,
            cod_cvm: str,
            start_date: date,
            end_date: date,
            participant_type: str,
            category: str,
            last_ref_date
    ):

        if (str(cod_cvm)) and (str(cod_cvm) is not None):
            cod_cvm = str(cod_cvm).zfill(6)

        if start_date and end_date:
            dataDe = start_date.strftime("%d/%m/%Y")
            dataAte = end_date.strftime("%d/%m/%Y")
            periodo = "2"
        else:
            dataDe = ""
            dataAte = ""
            periodo = "0"
        categoria = category
        ultimaDtRef = BOOL_STRING_MAPPER[last_ref_date]

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '324',
            'Content-Type': 'application/json; charset=UTF-8',
            'DNT': '1',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'x-dtpc': '28$428327064_275h18vMIPKIVDJMJWUHHIHJSUAWKKKMKVABKHO-0e0',
            'X-Requested-With': 'XMLHttpRequest'}

        data = "{" + f"""dataDe: '{dataDe}',
                dataAte: '{dataAte}' ,
                empresa: '{cod_cvm}',
                setorAtividade: '-1',
                categoriaEmissor: '-1',
                situacaoEmissor: '-1',
                tipoParticipante: '{participant_type}',
                dataReferencia: '',
                categoria: '{categoria}',
                periodo: '{periodo}',
                horaIni: '',
                horaFim: '',
                palavraChave:'',
                ultimaDtRef:'{ultimaDtRef}',
                tipoEmpresa:'0',
                token: '',
                versaoCaptcha: ''""" + "}"

        resp = self.session.post(
            self.LISTAR_DOCUMENTOS_URL, data=data, headers=headers, verify=False)
        return resp

    def get_reports(self, NumeroSequencialDocumento, CodigoTipoInstituicao, reports_list=None):
        url = f"{self.ENETCONSULTA_URL}frmGerenciaPaginaFRE.aspx?NumeroSequencialDocumento={NumeroSequencialDocumento}&CodigoTipoInstituicao={CodigoTipoInstituicao}"

        payload = {}
        headers = {}

        response = self.session.get(
            url, headers=headers, data=payload, verify=False)

        soup = BeautifulSoup(response.text, features="lxml")
        hdnNumeroSequencialDocumento = soup.find(
            id='hdnNumeroSequencialDocumento').attrs["value"]
        hdnCodigoTipoDocumento = soup.find(
            id='hdnCodigoTipoDocumento').attrs["value"]
        # hdnCodigoCvm = soup.find(id='hdnCodigoCvm').attrs["value"]
        # hdnDescricaoDocumento = soup.find(id='hdnDescricaoDocumento').attrs["value"]
        hdnCodigoInstituicao = soup.find(
            id='hdnCodigoInstituicao').attrs["value"]
        hdnHash = soup.find(id='hdnHash').attrs["value"]

        NumeroSequencialRegistroCvm = extract_substring(
            "NumeroSequencialRegistroCvm=", "&", response.text)

        end_of_report_url = f"&CodTipoDocumento={hdnCodigoTipoDocumento}&NumeroSequencialDocumento={hdnNumeroSequencialDocumento}&NumeroSequencialRegistroCvm={NumeroSequencialRegistroCvm}&CodigoTipoInstituicao={hdnCodigoInstituicao}&Hash={hdnHash}"

        reports = {}
        opt = str(BeautifulSoup(response.text,
                  features="lxml").find(id='cmbQuadro'))
        reports_options = BeautifulSoup(opt, features="lxml")
        reports_options = reports_options.find_all('option')

        if (reports_list is None):
            reports_list = [item.getText() for item in reports_options]

        for item in reports_options:
            if (item.getText() in reports_list):
                report_url = self.ENETCONSULTA_URL + \
                    item.attrs["value"] + end_of_report_url
                report_html_response = self.session.get(
                    report_url, headers=headers, verify=False)
                reports[item.getText()] = report_html_response

        return reports

    def get_enet_consulta_externa(self):
        consulta_enet_response = self.session.get(
            self.ENET_CONSULTA_EXTERNA, verify=False)
        return consulta_enet_response

    def get_cadastro_de_instrumentos_token(self, ref_date: date):
        ref_date = ref_date.strftime("%Y-%m-%d")

        token_url = f"https://arquivos.b3.com.br/api/download/requestname?fileName=InstrumentsConsolidated&date={ref_date}"
        response = self.session.get(token_url, verify=False)

        if response.ok:
            return response

    def get_cadastro_de_instrumentos(self, token: str):
        download_url = f"https://arquivos.b3.com.br/api/download/?token={token}"

        headers = {
            'authority': 'arquivos.b3.com.br',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1,',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }

        data = "{" + f"token: '{token}'" + "}"

        response = self.session.get(
            download_url,
            headers=headers,
            verify=False)

        if response.ok:
            return response

    def get_emissor(self):
        url = f"https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetFileDownload/NTE3ODA="
        response = self.session.get(url, verify=False)

        if response.ok:
            return response

    def get_pesquisa_cia_aberta(self):
        url = f"https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/ResultBuscaParticCiaAb.aspx?CNPJNome=&TipoConsult=C"
        response = self.session.get(url, verify=False)

        if response.ok:
            return response
