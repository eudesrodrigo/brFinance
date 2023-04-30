from datetime import date

from brfinance.connector import CVMHttpClientConnector
from brfinance.http_client import CVMHttpClient
from brfinance.responses import (
    GetCVMCodesResponse,
    GetCategoriesResponse,
    GetSearchResponse,
    GetReportResponse,
    GetTipoParticipanteResponse,
    GetCadastroInstrumentosTokenResponse,
    GetCadastroInstrumentosResponse,
    GetEmissorResponse,
    GetPesquisaCiaAbertaResponse
)

POOL_CONNECTOR = CVMHttpClientConnector()


class CVMAsyncBackend():

    def __init__(self) -> None:

        self._connector = POOL_CONNECTOR.get_connector()

    def _http_client(self):
        return CVMHttpClient(
            session=self._connector
        )

    def get_consulta_externa_cvm_results(
            self,
            start_date: date = None,
            end_date: date = None,
            cod_cvm: list = [],
            participant_type: list = [1],
            category: list = None,
            last_ref_date: bool = False
    ):

        if (not category) or (category is None):
            category = ['EST_-1', 'IPE_-1_-1_-1']

        if (not participant_type) or (participant_type is None):
            participant_type = ['-1']

        response = self._http_client().get_search_results(
            cod_cvm=cod_cvm,
            start_date=start_date,
            end_date=end_date,
            category=",".join(category),
            participant_type=str(
                ",".join([str(item) for item in participant_type])),
            last_ref_date=last_ref_date)
        response_class = GetSearchResponse(response=response)

        return response_class.data()

    def get_report(
            self,
            NumeroSequencialDocumento,
            CodigoTipoInstituicao,
            reports_list=None,
            previous_results=False):
        response = self._http_client().get_reports(
            NumeroSequencialDocumento,
            CodigoTipoInstituicao,
            reports_list)
        response_class = GetReportResponse(response=response, previous_results=previous_results)

        return response_class.data()

    def get_cvm_codes(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetCVMCodesResponse(response=response)

        return response_class.data()

    def get_consulta_externa_cvm_categories(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetCategoriesResponse(response=response)

        return response_class.data()

    def get_consulta_externa_cvm_tipo_participante(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetTipoParticipanteResponse(response=response)

        return response_class.data()

    def get_consulta_externa_cvm_categories(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetCategoriesResponse(response=response)

        return response_class.data()

    def get_cadastro_instrumentos(self, ref_date: date = date.today()):

        token_response = self._http_client(
        ).get_cadastro_de_instrumentos_token(ref_date=ref_date)
        token = GetCadastroInstrumentosTokenResponse(
            response=token_response).data()

        response = self._http_client().get_cadastro_de_instrumentos(token=token)
        response_class = GetCadastroInstrumentosResponse(response=response)

        return response_class.data()

    def get_emissor(self):

        response = self._http_client().get_emissor()
        response_class = GetEmissorResponse(response=response)

        return response_class.data()

    def get_pesquisa_cia_aberta(self):

        response = self._http_client().get_pesquisa_cia_aberta()
        response_class = GetPesquisaCiaAbertaResponse(response=response)

        return response_class.data()
