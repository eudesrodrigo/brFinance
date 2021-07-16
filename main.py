import brFinance

#driver = dadosFinanceirosBr.iniciarChromeDriver()
#search_enet_object = dadosFinanceirosBr.SearchENET(cod_cvm=21610, category=21)

b3 = brFinance.Company(cod_cvm=21610)

print(b3.reports)