import unittest
import sys
sys.path.append('../')
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
working_dir = os.path.join(current_dir , "..")
import sys
sys.path.append(working_dir)
import brFinance.scraper as scraper
from pandas import DataFrame, Index

import brFinance.utils as utils
from datetime import date

class TestSearchENET(unittest.TestCase):
    """
    tests for class SearchENET from module scraper
    """

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()


    @classmethod
    def tearDownClass(cls) -> None:
        return super().setUpClass()


    def setUp(self):
        self.driver = utils.Browser.run_chromedriver()
        self.search_enet_object = scraper.SearchENET(cod_cvm=21610, category=21, driver=self.driver)


    def tearDown(self) -> None:
        self.driver.quit()
        return super().tearDown()


    def test_search(self):
        """
        Tests method get_search_results
        """

        # Tests method get_search_results result for right categories type (21 and 39)
        self.assertIsInstance(self.search_enet_object.search, DataFrame, msg="get_search_results returned does not returned a Pandas DataFrame for categoria=21.")
        
        # Tests if search dataframe has the right columns
        results_columns = ['Código CVM', 'Empresa', 'Categoria', 'Tipo', 'Espécie', 'Data Referência', 'Data Entrega', 'Status', 'V', 'Modalidade', 'linkView', 'linkDownload']
        self.assertEqual(list(self.search_enet_object.search.columns), results_columns, msg="Wrong columns in the financial_reports_search_result ")

        #Tests if search dataframe has values
        results_counter = len(self.search_enet_object.search)
        self.assertGreater(results_counter, 0, msg="No results found to cod_cvm = 21610 and category=21")

        self.search_enet_object.category = 39
        # Tests if search is a dataframe
        self.assertIsInstance(self.search_enet_object.search, DataFrame, msg="get_search_results returned does not returned a Pandas DataFrame for categoria=21.")

        # Tests if search dataframe has the right columns
        results_columns = ['Código CVM', 'Empresa', 'Categoria', 'Tipo', 'Espécie', 'Data Referência', 'Data Entrega', 'Status', 'V', 'Modalidade', 'linkView', 'linkDownload']
        self.assertEqual(list(self.search_enet_object.search.columns), results_columns, msg="Wrong columns in the financial_reports_search_result ")

        #Tests if search dataframe has values
        results_counter = len(self.search_enet_object.search)
        self.assertGreater(results_counter, 0, msg="No results found to cod_cvm = 21610 and category=21")
    

    def test_assert_raises(self):

        # Test if raises exception for invalid CVM code
        self.assertRaises(ValueError, scraper.SearchENET, cod_cvm=2, category=21)


        # Test if raises exception for invalid category
        self.assertRaises(ValueError, scraper.SearchENET, cod_cvm=21610, category=5000)
        # Tests method get_search_results result for wrong category type (30 does not exist)
        #self.assertIsInstance(search_enet_object.get_search_results(categoria="30"), DataFrame, msg="wait_load returned less than 0 for tabela_resultados.")


class TestUtilsDates(unittest.TestCase):
    """
    tests for class Dates from module utils
    """
    
    def test_previous_quarter_end_date(self):
        """
        Tests method previous_quarter_end_date
        """

        date_obj = utils.Dates(date(2021, 7, 12))
        quarter_end = date_obj.previous_quarter_end_date
        self.assertIsInstance(quarter_end, date, msg="Wrong return type for previous_quarter_end_date.")

        self.assertEqual(quarter_end, date(2021, 6, 30), msg=f"Return date to previous quarter end of 2021-7-12 is wrong:{quarter_end}")


if __name__ == '__main__':
    unittest.main()
    
    