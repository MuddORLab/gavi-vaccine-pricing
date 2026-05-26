#!/usr/bin/env python

# Run via `python run_params.py` to just execute the `params.py` file
# Debug using print statements, etc.

import gavi.params.params as params

print('Avg competing price:')
print(params.avg_competing_price)

print('Demand intercept:')
print(params.demand_intercept)

print('Historical demand:')
print(params.hist_demand)

print('Projected demand:')
print(params.demand_projection)

print('Competition matrix')
print(params.vaccine_competition)

print('Dataframe grouped by year, vaccine product, prices are summed')
print(params.df_vaccine_prices_year_and_vaccine)

print('Dataframe grouped by year, vaccine product: prices are summed')
print(params.df_vaccine_prices)

print('Dataframe grouped by year, vaccine product: gives the number of distinct vaccine products')
print(params.df_vaccine_mfrs)

print('Dataframe grouped by year, vaccine product: gives the number of distinct vaccine products')
print(params.df_vaccine_demand)

# print('Filtered Dataframe')
# print(params.df_vaccine_purchase)

# print('Price per antigen')
# print(params.price_per_antigen)

# TODO: future cleanup things
# print('Upper price:')
# print(params.historical_upper_price_limit)

# print('Profit threshold:')
# print(params.profit_threshold)
