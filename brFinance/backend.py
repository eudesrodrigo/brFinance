from datetime import date

from brfinance.connector import CVMHttpClientConnector
from brfinance.http_client import CVMHttpClient
from brfinance.responses import (
    GetCVMCodesResponse,
    GetCategoriesResponse,
    GetSearchResponse,
    GetReportResponse
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
            self, cod_cvm, start_date: date, end_date: date, last_ref_date: bool, report_type: str
            ):

        response = self._http_client().get_search_results(
            cod_cvm=cod_cvm,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            last_ref_date=last_ref_date)
        response_class = GetSearchResponse(response=response)

        return response_class.data()

    def get_report(
            self,
            NumeroSequencialDocumento,
            CodigoTipoInstituicao,
            reports_list=None):
        response = self._http_client().get_reports(
            NumeroSequencialDocumento,
            CodigoTipoInstituicao,
            reports_list)
        response_class = GetReportResponse(response=response)

        return response_class.data()

    def get_cvm_codes(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetCVMCodesResponse(response=response)

        return response_class.data()

    def get_consulta_externa_cvm_categories(self):
        response = self._http_client().get_enet_consulta_externa()
        response_class = GetCategoriesResponse(response=response)

        return response_class.data()
