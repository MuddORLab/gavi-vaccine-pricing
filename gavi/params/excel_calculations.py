import pandas as pd



# excel_demand = pd.ExcelFile('Detailed Demand Forecast_crosstab.xlsx')
# df_demand = pd.read_excel(excel_demand, 'GAVI Hex Demand')



# Can access prices like
# df_vaccine_prices[2015]['BCG']['Japan BCG Laboratory']

# print(df[['Group']]) 
# print(df["Group"])
# print(df['Gavi/Non-Gavi'] == 'Gavi')
list_of_vaccine_subtypes = ['DTaP', 
                            'DTwP', 
                            'HepB (ped.)', 
                            'IPV', 
                            'bOPV', 
                            'mOPV1', 
                            'mOPV2', 
                            'mOPV3', 
                            'tOPV', 
                            'DTaP-HepB-Hib-IPV',
                            'DTaP-IPV',
                            'DTwP-HepB',
                            'DTwP-HepB-Hib',
                            'DTwP-HepB-Hib-IPV']

antigens_per_subtype =      ['1', 
                            '1', 
                            '1', 
                            '1', 
                            '1', 
                            '1', 
                            '1', 
                            '1', 
                            '1', 
                            '4',
                            '2',
                            '2',
                            '3',
                            '4']

competing_products_by_vaccine = [['DTaP-HepB-Hib-IPV', 'DTaP-IPV', 'DTwP-HepB', 'DTwP-HepB-Hib', 'DTwP-HepB-Hib-IPV'], # DTP
                                ['DTaP-HepB-Hib-IPV', 'DTwP-HepB', 'DTwP-HepB-Hib', 'DTwP-HepB-Hib-IPV'],  # HepB
                                ['bOPV', 'mOPV1', 'mOPV2', 'mOPV3', 'tOPV', 'DTaP-HepB-Hib-IPV','DTaP-IPV','DTwP-HepB-Hib-IPV'],  # IPV
                                ['IPV', 'DTaP-HepB-Hib-IPV', 'DTaP-IPV', 'DTwP-HepB-Hib-IPV'],  # OPV
                                ['DTaP', 'DTwP', 'HepB (ped.)', 'DTaP-HepB-Hib-IPV','DTaP-IPV','DTwP-HepB','DTwP-HepB-Hib','DTwP-HepB-Hib-IPV'],  # Pent
                                ['DTaP', 'DTwP', 'HepB (ped.)', 'IPV', 'bOPV', 'mOPV1', 'mOPV2', 'mOPV3', 'tOPV', 'DTaP-HepB-Hib-IPV','DTaP-IPV','DTwP-HepB','DTwP-HepB-Hib','DTwP-HepB-Hib-IPV'],  # Hex
                                ['DTaP', 'DTwP', 'IPV', 'bOPV', 'mOPV1', 'mOPV2', 'mOPV3', 'tOPV', 'DTaP-HepB-Hib-IPV','DTaP-IPV','DTwP-HepB','DTwP-HepB-Hib','DTwP-HepB-Hib-IPV'],  # DTP-IPV
                                ['DTaP', 'DTwP', 'HepB (ped.)', 'DTaP-HepB-Hib-IPV','DTaP-IPV','DTwP-HepB','DTwP-HepB-Hib','DTwP-HepB-Hib-IPV']  # DTP-HepB
                                ]

# in params.py:
    # vaccine_name_mapper = {
    #     "DTaP": "DTP",
    #     "DTwP": "DTP",
    #     "HepB (ped.)": "HepB",
    #     "IPV": "IPV",
    #     "bOPV": "OPV",
    #     "mOPV1": "OPV",
    #     "mOPV2": "OPV",
    #     "mOPV3": "OPV",
    #     "tOPV": "OPV",
    #     "DTwP-HepB-Hib": "Pent",
    #     "DTaP-HepB-Hib-IPV": "Hex",
    #     "DTwP-HepB-Hib-IPV": "Hex",
    #     "DTaP-IPV": "DTP-IPV",
    #     "DTwP-HepB": "DTP-HepB"
    # }

    # vaccine_names = ["DTP", "HepB", "IPV", "OPV", "Pent", "Hex", "DTP-IPV", "DTP-HepB"]

def create_df_vaccine_prices():
    excel_vaccine_purchase = pd.ExcelFile('mi4a_public_database.xlsx')
    df_vaccine_purchase = pd.read_excel(excel_vaccine_purchase, 'Vaccine Purchase Data')
    df_vaccine_purchase = df_vaccine_purchase[[
        'Gavi/Non-Gavi',
        'Year',
        'Vaccine Sub-type',
        'Manufacturer',
        'Annual Number of Doses',
        'Price per Dose in USD'
    ]]
    df_vaccine_purchase= df_vaccine_purchase[
        (df_vaccine_purchase['Gavi/Non-Gavi'] == 'Gavi') &
        (df_vaccine_purchase['Year'] >= 2015) &
        (df_vaccine_purchase['Vaccine Sub-type'] in list_of_vaccine_subtypes) 
    ]
    df_vaccine_prices = df_vaccine_purchase.groupby([
        ''
    ])
    df_vaccine_prices = df_vaccine_purchase.groupby([
        'Year',
        'Vaccine Sub-type',
        'Manufacturer'
    ])['Price per Dose in USD'].max() # filter out entries with no listed prices
    return df_vaccine_prices

# __________ cost terms __________

# cost term calculation per vaccine, year:
# n^v * (sum over mfr: price of v/antigen in v + sum over mfr: price of all competing v' != v/antigen in v)/competing products for v 

# input v, v', t
#
# num_antigens[v] * [
#     ( sum over mfr i: price[v,i,t] / num_antigens[v] ) +
#     ( sum over mfr i: price[v',i,t] / num_antigens[v'] )
# ] / competing_products[v]

create_df_vaccine_prices()

avg_competing_price = np.zeros((6, V))
price_per_antigen = np.zeros(len(list_of_vaccine_subtypes))

# calculate price per antigen for all vaccine subtypes
for i in ['2015', '2016', '2017', '2018', '2019', '2020']: # for each year
    for j in list_of_vaccine_subtypes: # for each vaccine subtype
        price_per_antigen[j] = df_vaccine_prices[i][j].sum()['Price per Dose in USD']/antigens_per_subtype[j]

# calculate avg competing price for all vaccine products
for i in ['2015', '2016', '2017', '2018', '2019', '2020']: # for each year    
    for k in range(V): # for each vaccine product
        for c in competing_products_by_vaccine:
            avg_competing_price[i][k] = num_antigens[k] * [
                price_per_antigen[price_per_antigen.index([p for p, v in vaccine_name_mapper.items() if v == vaccine_names[k]])] +
                price_per_antigen[price_per_antigen.index(c)] # price per antigen of competing products
            ] / vaccine_competition[:,k].sum() # divide by total number of competing products
        
        
        # avg_competing_price[i][j] = num_antigens[j] * [
        #     df_vaccine_prices[i][j].sum()['Price per Dose in USD']/num_antigens[j] + # sum prices across all mfr 
        #     df_vaccine_prices[i][j].sum()['Price per Dose in USD']/num_antigens[j]
        # ] / competing_products[v]

# __________ hist demand __________

# compute for each vaccine product, each year 2015-2020

# __________ proj demand __________

# compute for each vaccine product, each year 2024-2030