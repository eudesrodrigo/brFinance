from selenium import webdriver
import platform
from fake_useragent import UserAgent
import os
from webdriver_manager.chrome import ChromeDriverManager

from datetime import date
import math
from dateutil.relativedelta import relativedelta
import time

import pandas as pd
from dataclasses import dataclass

@dataclass
class Browser:

    def download_wait(path_to_downloads):
        """
        Waits all Chrome download files (.crdownload) in a folder be done before continues
        """
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < 20:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(path_to_downloads):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds

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
            prefs = {"download.default_directory": root + "/downloads"}
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


@dataclass
class File:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        
    def check_exist(self) -> bool:
        if os.path.isfile(self):
            return True
        else:
            return False
    
    def create_folder(self) -> None:
        try:
            os.makedirs(self)
        except FileExistsError:
            # directory already exists
            pass

@dataclass
class Dates:
    def __init__(self, _date: date):
        self.date = _date
    
    @property
    def previous_quarter_end_date(self) -> date:
        return (self.date - relativedelta(months=3) - pd.tseries.offsets.DateOffset(day=1) + pd.tseries.offsets.QuarterEnd()).date()


if __name__ == '__main__':
    print(Dates(date(2021, 7, 12)).previous_quarter_end_date)