from .constants import ENET_URL


def extract_substring(start, end, string):
    return string.split(start)[-1].split(end)[0]


def get_enet_download_url(numSequencia, numVersao, numProtocolo, descTipo):
    return ENET_URL + f"frmDownloadDocumento.aspx?Tela=ext&numSequencia={numSequencia}&numVersao={numVersao}&numProtocolo={numProtocolo}-79&descTipo={descTipo}&CodigoInstituicao=1"
