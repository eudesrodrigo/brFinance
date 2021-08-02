import os
import platform
from time import sleep
from dataclasses import dataclass
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

DOWNLOAD_PATH = root = os.path.dirname(os.path.abspath(__file__)) + "/downloads"

@dataclass
class Browser:

    @staticmethod
    def download_wait(path_to_downloads: str=DOWNLOAD_PATH):
        """
        Waits all Chrome download files (.crdownload) in a folder be done before continues
        """
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < 20:
            sleep(1)
            dl_wait = False
            for fname in os.listdir(path_to_downloads):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds

    @staticmethod
    def run_chromedriver(hidden: bool=True) -> webdriver:
        """
        Instantiate a webdriver object with different settings depending of OS you are using
        """

        os.environ['WDM_LOG_LEVEL'] = '0'
        system = str(platform.system())
        
        if system == "Windows" or system == "Darwin":
            # Options for windows
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            if hidden:
                options.add_argument("--headless")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--incognito")
            options.add_argument('user-agent={userAgent}'.format(userAgent=UserAgent().chrome))
            root = os.path.dirname(os.path.abspath(__file__))
            prefs = {"download.default_directory": DOWNLOAD_PATH}
            options.add_experimental_option("prefs", prefs)

            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        else:
            # Options for linux
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument("--headless")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--incognito")
            options.add_argument('user-agent={userAgent}'.format(userAgent=UserAgent().chrome))

            driver = webdriver.Chrome(options=options)

        return driver