from brFinance.scraper.cvm.company import Company

# Instantiate object for Petrobras (Cod. CVM = 9512)
petrobras = Company(cvm_code=9512)

# Get useful information about Petrobras
print(petrobras.get_social_capital_data())
print(petrobras.get_registration_data())

# Get annual and quarterly reports separately
annual_reports = petrobras.get_annual_reports()
quarterly_reports = petrobras.get_quarterly_reports()

# Or both together
annual_reports, quarterly_reports = petrobras.get_all_reports()

# Getting data
print(quarterly_reports["31/03/2021"]["Demonstração do Resultado"])

# Get available dates
print(annual_reports.keys())
print(quarterly_reports.keys())

# Get available report for each date
print(quarterly_reports["31/03/2021"].keys())
