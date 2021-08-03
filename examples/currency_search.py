from brFinance.scraper.bacen.currency import Currency

# Show all available currencies in Brazilian Central Bank and their respective codes
print(Currency.get_available_currencies())

# Show today prices for all currencies in respect to Brazilian Real
print(Currency.get_today_prices())

# Searching for a specific currency and period
dolar = Currency(currency_code=61, initial_date="26/07/2021", final_date="02/08/2021")

print(dolar.get_price())
