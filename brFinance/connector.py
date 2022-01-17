from requests import Session
import requests

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass


class CVMHttpClientConnector():

    def __init__(self) -> None:
        self.CONNECTOR = Session()

    def get_connector(self):
        return self.CONNECTOR
