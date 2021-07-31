from brFinance.scraper.cvm.search import SearchDFP, SearchITR

# ENET search for each available category
search_dfp = SearchDFP()  # Demonstração Financeira Padronizada
search_itr = SearchITR()  # Informações Trimestrais

available_annual_records = search_dfp.search(9512)
print(available_annual_records)

# Get all CVM codes available
print(search_dfp.get_cvm_codes())
