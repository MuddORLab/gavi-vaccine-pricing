"""Create parameter grid and identify each trial uniquely.
Modify for sensitivity analysis.
"""

from ..trials.types import MultiParam, lambda_multi_param

# Multi-params can be created like so
# x = 5
# x = MultiParam([5, 6, 7])

import numpy as np
import pandas as pd

# ------------------ Scaling ------------------------------------

MIL = 1             # 1 million scaled
BIL = MIL * 10**3   # 1 billion scaled
N = 1000            # 1000
N1 = 10**6          # 1 million
N2 = 100            # 100

# ------------------ Lists, etc. for indexing ------------------------------------

# Dictionary of vaccine subtypes as they appear in the spreadsheet to names, grouped into vaccine products as in the model
vaccine_name_mapper = {
    "DTaP": "DTP",
    "DTwP": "DTP",
    "HepB (ped.)": "HepB",
    "IPV": "IPV",
    "bOPV": "OPV",
    "mOPV1": "OPV",
    "mOPV2": "OPV",
    "mOPV3": "OPV",
    "tOPV": "OPV",
    "DTwP-HepB-Hib": "Pent",
    "DTWP-HepB-Hib": "Pent",
    "DTaP-HepB-Hib-IPV": "Hex",
    "DTwP-HepB-Hib-IPV": "Hex",
    "DTaP-IPV": "DTP-IPV",
    "DTwP-HepB": "DTP-HepB"
}

vaccine_names = ["DTP", "HepB", "IPV", "OPV", "Pent", "Hex", "DTP-IPV", "DTP-HepB"]
antigen_names = ["DTP", "HepB", "Hib", "Polio"]
num_antigens =  [1,     1,      1,      1,      3,      4,      2,      2]  # number of antigens in each vaccine product

M = 20      # starting number of mfrs
T = 7       # starting length of tender (years)
V = len(vaccine_names)       # starting number of vaccine products 
A = len(antigen_names)       # number of antigens

# ------------------ Excel helpers ------------------------------------

def create_df_vaccine_prices():
    excel_vaccine_purchase = pd.ExcelFile('mi4a_public_database.xlsx')
    df_vaccine_purchase = pd.read_excel(excel_vaccine_purchase, 'Vaccine Purchase Data')

    df_vaccine_purchase['Vaccine Type'] = df_vaccine_purchase['Vaccine Sub-type'].map(vaccine_name_mapper)
    df_vaccine_purchase = df_vaccine_purchase[[
        'Gavi/Non-Gavi',
        'Year',
        'Vaccine Type',
        'Manufacturer',
        'Annual Number of Doses',
        'Price per Dose in USD',
    ]] 
    # filter by Gavi, 2015 onward, relevant vaccine products
    df_vaccine_purchase = df_vaccine_purchase[
        (df_vaccine_purchase['Gavi/Non-Gavi'] == 'Gavi') &
        (df_vaccine_purchase['Year'] >= 2015) & 
        (df_vaccine_purchase['Vaccine Type'].isin(vaccine_names))
    ]
    # only include if there is a listed price
    df_vaccine_purchase.dropna()
    # only include if price not 0
    df_vaccine_purchase = df_vaccine_purchase[df_vaccine_purchase['Price per Dose in USD'] != 0]
    
    # prices summed over all mfrs
    df_vaccine_prices = df_vaccine_purchase.groupby([
        'Year',
        'Vaccine Type',
        # 'Manufacturer',
        # 'Annual Number of Doses'
    ])['Price per Dose in USD'].sum() 
    
    # demand summed over all mfrs
    df_vaccine_demand = df_vaccine_purchase.groupby([ 
        'Year',
        'Vaccine Type',
        # 'Manufacturer',
        # 'Price per Dose in USD'
    ]) ['Annual Number of Doses'].sum() 
    
    # to calculate total # of products, first simplify information in df
    df_vaccine_purchase_for_mfr_calculation = df_vaccine_purchase[[
        'Year',
        'Vaccine Type',
        'Manufacturer',
    ]] 
    # lumping together all vaccine products with same year, vaccine type, and mfr
    df_vaccine_purchase_for_mfr_calculation = df_vaccine_purchase_for_mfr_calculation.drop_duplicates()

    # total number of products (distinguished by manufacturer)
    df_vaccine_mfrs = df_vaccine_purchase_for_mfr_calculation.groupby([ 
        'Year',
        'Vaccine Type',
    ]) ['Manufacturer'].count() 
    # df_vaccine_mfrs = df_vaccine_mfrs.groupby([ 
    #     'Year',
    #     'Vaccine Type',
    #     'Manufacturer',
    # ]) ['Annual Number of Doses'].count() 
        # 'Manufacturer'
        # ]]
    return df_vaccine_prices, df_vaccine_demand, df_vaccine_mfrs, df_vaccine_purchase

# if a vaccine product is produced in multiple forms by the same manufacturer, we effectively consider as one product
# by averaging the prices and also only counting unique year-product-mfr combinations

# ------------------ Specify parameter values for sensitivity analysis ------------------------------------

profit_scaling_factor = MultiParam([1])
gamma = 0.5 # gamma for b, c
hex_proportion = MultiParam([0.01, 0.05]) # proportion of demand per antigen to be met by hexavalent
opv_frac = MultiParam([1/3, 2/3])   # fraction of demand for polio going to OPV

def create_hex_cost(default_value, penta_and_ipv_value):
    result = [default_value] * M
    # cost = 0 for mfrs who already produce Hexa (17 and 18)
    result[16], result[17] = 0, 0      
    # cost half for mfrs who already produce Penta and IPV (16 and 19) 
    result[15], result[18] = penta_and_ipv_value, penta_and_ipv_value       
    return result

hex_cost = MultiParam([
    create_hex_cost(100, 50),
    create_hex_cost(90, 45),
])

                                                #   DTP   HepB   IPV   OPV   Pent  Hex   DTP-IPV  DTP-HepB
historical_upper_price_limit = MultiParam([np.array([0.45, 1.81, 4.73, 2.06, 2.65, 207,  17.7,    2.3]),
                             10*np.array([0.45, 1.81, 4.73, 2.06, 2.65, 207,  17.7, 2.3])
                          ])

demand_projection = MultiParam([ np.array([
    [196.577949*MIL,    200.295609*MIL,     203.776515*MIL,     207.197014*MIL,     210.249261*MIL,     213.249984*MIL,     216.196634*MIL],        # DTP
    [220.726573*MIL,    224.846562*MIL,     228.913068*MIL,     232.857313*MIL,     236.405680*MIL,     239.868796*MIL,     243.251377*MIL],        # HepB
    [190.504523*MIL,    194.244332*MIL,     197.777238*MIL,     201.155884*MIL,     204.226794*MIL,     207.232195*MIL,     210.188594*MIL],        # Hib
    [391.456441*MIL,    401.202911*MIL,     408.983746*MIL,     117.911386*MIL,     120.180762*MIL,     122.415286*MIL,     124.566235*MIL],        # Polio
]), # Original demand 
                                np.array([
    [196.577949*MIL,    200.295609*MIL,     203.776515*MIL,     207.197014*MIL,     210.249261*MIL,     213.249984*MIL,     216.196634*MIL],        # DTP
    [220.726573*MIL,    224.846562*MIL,     228.913068*MIL,     232.857313*MIL,     236.405680*MIL,     239.868796*MIL,     243.251377*MIL],        # HepB
    [190.504523*MIL,    194.244332*MIL,     197.777238*MIL,     201.155884*MIL,     204.226794*MIL,     207.232195*MIL,     210.188594*MIL],        # Hib
    [391.456441*MIL,    401.202911*MIL,     408.983746*MIL,     416.7890637*MIL,	424.5783354*MIL,	432.4347005*MIL,	440.311319*MIL],        # Polio
])  # Polio extrapolation
                                 ])

mfr_resources2 = MultiParam([ np.array([
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 1 AJ Vaccines A/S
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 2 Beijing Institute of Biological Products Co., Ltd.  (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 3 Bharat Biotech International Limited
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 4 Bilthoven Biologicals
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 5 Bio-Med
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 6 Biological E. Limited
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 7 Boryung
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 8 Changchun Keygen Biological Products Co.,Ltd (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 9 GlaxoSmithKline Biologicals SA
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 10 Indian Immunologicals Ltd
    [1,	    0,	    0,	    0,	    0,	    0,	    0,	     0],	# 11 Institute of Vaccines and Medical Biologicals, Vietnam
    [0,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 12 LG Chem Ltd
    [0,	    0,	    0,	    0,	    1,	    0,	    0,	     0],	# 13 Panacea Biotec Ltd.
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 14 POLYVAC (Center for Research and production of Vaccine and Biologicals)
    [0,	    1,	    0,	    1,	    1,	    0,	    0,	     0],	# 15 PT Bio Farma (Persero)
    [0,	    0,	    1,	    0,	    1,	    0,	    0,	     0],	# 16 Sanofi Healthcare India Private Limited
    [0,	    0,	    1,	    1,	    0,	    1,	    1,	     0],	# 17 Sanofi Pasteur
    [1,	    1,	    0,	    1,	    1,	    1,	    0,	     1],	# 18 Serum Institute of India Pvt. Ltd.
    [0,	    1,	    1,	    1,	    1,	    0,	    0,	     1],	# 19 Shantha Biotechnics Private Limited (A Sanofi Company)
    [0,	    1,	    0,	    0,	    0,	    0,	    0,	     0]	    # 20 VABIOTECH
]), # historical production of hexavalent
                             np.array([
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 1 AJ Vaccines A/S
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 2 Beijing Institute of Biological Products Co., Ltd.  (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 3 Bharat Biotech International Limited
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 4 Bilthoven Biologicals
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 5 Bio-Med
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 6 Biological E. Limited
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 7 Boryung
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 8 Changchun Keygen Biological Products Co.,Ltd (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 9 GlaxoSmithKline Biologicals SA
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 10 Indian Immunologicals Ltd
    [1,	    0,	    0,	    0,	    0,	    0,	    0,	     0],	# 11 Institute of Vaccines and Medical Biologicals, Vietnam
    [0,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 12 LG Chem Ltd
    [0,	    0,	    0,	    0,	    1,	    0,	    0,	     0],	# 13 Panacea Biotec Ltd.
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 14 POLYVAC (Center for Research and production of Vaccine and Biologicals)
    [0,	    1,	    0,	    1,	    1,	    0,	    0,	     0],	# 15 PT Bio Farma (Persero)
    [0,	    0,	    1,	    0,	    1,	    1,	    0,	     0],	# 16 Sanofi Healthcare India Private Limited
    [0,	    0,	    1,	    1,	    0,	    1,	    1,	     0],	# 17 Sanofi Pasteur
    [1,	    1,	    0,	    1,	    1,	    1,	    0,	     1],	# 18 Serum Institute of India Pvt. Ltd.
    [0,	    1,	    1,	    1,	    1,	    1,	    0,	     1],	# 19 Shantha Biotechnics Private Limited (A Sanofi Company)
    [0,	    1,	    0,	    0,	    0,	    0,	    0,	     0]	    # 20 VABIOTECH
]), # historical production and pent+IPV manufacturers produce hexavalent
                             np.array([
    [0,	    0,	    1,	    0,	    0,	    1,	    0,	     0],	# 1 AJ Vaccines A/S
    [0,	    0,	    0,	    1,	    0,	    1,	    0,	     0],	# 2 Beijing Institute of Biological Products Co., Ltd.  (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    1,	    0,	     0],	# 3 Bharat Biotech International Limited
    [0,	    0,	    1,	    0,	    0,	    1,	    0,	     0],	# 4 Bilthoven Biologicals
    [0,	    0,	    0,	    1,	    0,	    1,	    0,	     0],	# 5 Bio-Med
    [1,	    1,	    0,	    0,	    1,	    1,	    0,	     0],	# 6 Biological E. Limited
    [0,	    0,	    0,	    1,	    0,	    1,	    0,	     0],	# 7 Boryung
    [0,	    0,	    0,	    1,	    0,	    1,	    0,	     0],	# 8 Changchun Keygen Biological Products Co.,Ltd (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    1,	    0,	     0],	# 9 GlaxoSmithKline Biologicals SA
    [1,	    1,	    0,	    0,	    1,	    1,	    0,	     0],	# 10 Indian Immunologicals Ltd
    [1,	    0,	    0,	    0,	    0,	    1,	    0,	     0],	# 11 Institute of Vaccines and Medical Biologicals, Vietnam
    [0,	    1,	    0,	    0,	    1,	    1,	    0,	     0],	# 12 LG Chem Ltd
    [0,	    0,	    0,	    0,	    1,	    1,	    0,	     0],	# 13 Panacea Biotec Ltd.
    [0,	    0,	    0,	    1,	    0,	    1,	    0,	     0],	# 14 POLYVAC (Center for Research and production of Vaccine and Biologicals)
    [0,	    1,	    0,	    1,	    1,	    1,	    0,	     0],	# 15 PT Bio Farma (Persero)
    [0,	    0,	    1,	    0,	    1,	    1,	    0,	     0],	# 16 Sanofi Healthcare India Private Limited
    [0,	    0,	    1,	    1,	    0,	    1,	    1,	     0],	# 17 Sanofi Pasteur
    [1,	    1,	    0,	    1,	    1,	    1,	    0,	     1],	# 18 Serum Institute of India Pvt. Ltd.
    [0,	    1,	    1,	    1,	    1,	    1,	    0,	     1],	# 19 Shantha Biotechnics Private Limited (A Sanofi Company)
    [0,	    1,	    0,	    0,	    0,	    1,	    0,	     0]	    # 20 VABIOTECH
]) # anyone can produce hexavalent 
                            ])

excluded_mfrs = []  
# 0 AJ, 1 Beijing, 2 Bharat, 3 Bilthoven, 4 Bio-Med, 5 Bio E, 6 Boryung, 7 Changchun, 8 Glaxo, 9 Indian Immun, 10 Inst (Viet)
# 11 LG Chem, 12 Panacea, 13 POLYVAC, 14 PT Bio, 15 Sanofi Health, 16 Sanofi Pasteur, 17 SII, 18 Shantha, 19 VABIOTECH

excluded_years = []
# YEARS: 0 2024, 1 2025, 2 2026, 3 2027, 4 2028, 5 2029, 6 2030

excluded_vaccines = []      # input indices of vaccines to exclude
# VACCINES: 0 DTP, 1 HepB, 2 IPV, 3 OPV, 4 Pent, 5 Hex, 6 DTP-IPV, 7 DTP-HepB

# NOTE: issue with excluding DTP/Pent, see constraints_rows_to_exclude

# ------------------ Toggle trial type ------------------------------------

STANDARD = 1

# ------------------ Global trial inputs (maxes are inclusive) ------------------------------------

#   DTP   HepB  IPV   OPV    Pent  Hex    DTP-IPV  DTP-HepB
vaccine_composition = np.array([  
    [1,   0,    0,    0,     1,    1,      1,      1],     # DTP
    [0,   1,    0,    0,     1,    1,      0,      1],     # HepB
    [0,   0,    0,    0,     1,    1,      0,      0],     # Hib
    [0,   0,    1,    1,     0,    1,      1,      0],     # Polio
])

# vaccine A competes with vaccine B if there exists an antigen they both contain
# take dot product of two columns from vaccine_composition
# if vaccines compete, then the dot product is nonzero
vaccine_competition = np.empty((V, V))
for i in range(V):
    for j in range(V):
        vaccine_competition[i, j] = np.dot(vaccine_composition[:,i], vaccine_composition[:,j]) != 0
vaccine_competition -= np.identity(V) # to exclude itself
vaccine_competition_self = vaccine_competition + np.identity(V)

#   DTP	    HepB    IPV	    OPV	    Pent	Hex	    DTP-IPV	 DTP-HepB   
mfr_resources = np.array([
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 1 AJ Vaccines A/S
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 2 Beijing Institute of Biological Products Co., Ltd.  (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 3 Bharat Biotech International Limited
    [0,	    0,	    1,	    0,	    0,	    0,	    0,	     0],	# 4 Bilthoven Biologicals
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 5 Bio-Med
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 6 Biological E. Limited
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 7 Boryung
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 8 Changchun Keygen Biological Products Co.,Ltd (CNBG Subsidiary)
    [0,	    0,	    0,	    1,	    1,	    0,	    0,	     0],	# 9 GlaxoSmithKline Biologicals SA
    [1,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 10 Indian Immunologicals Ltd
    [1,	    0,	    0,	    0,	    0,	    0,	    0,	     0],	# 11 Institute of Vaccines and Medical Biologicals, Vietnam
    [0,	    1,	    0,	    0,	    1,	    0,	    0,	     0],	# 12 LG Chem Ltd
    [0,	    0,	    0,	    0,	    1,	    0,	    0,	     0],	# 13 Panacea Biotec Ltd.
    [0,	    0,	    0,	    1,	    0,	    0,	    0,	     0],	# 14 POLYVAC (Center for Research and production of Vaccine and Biologicals)
    [0,	    1,	    0,	    1,	    1,	    0,	    0,	     0],	# 15 PT Bio Farma (Persero)
    [0,	    0,	    1,	    0,	    1,	    0,	    0,	     0],	# 16 Sanofi Healthcare India Private Limited
    [0,	    0,	    1,	    1,	    0,	    1,	    1,	     0],	# 17 Sanofi Pasteur
    [1,	    1,	    0,	    1,	    1,	    1,	    0,	     1],	# 18 Serum Institute of India Pvt. Ltd.
    [0,	    1,	    1,	    1,	    1,	    0,	    0,	     1],	# 19 Shantha Biotechnics Private Limited (A Sanofi Company)
    [0,	    1,	    0,	    0,	    0,	    0,	    0,	     0]	    # 20 VABIOTECH
])

#   DTP	    HepB	IPV	    OPV	    Pent	Hex	    DTP-IPV	DTP-HepB
constraints = np.array([
    [1,	    0,	    0,	    0,	    1,	    1,	    1,	    1],	    # DTP
    [0,	    1,	    0,	    0,	    1,	    1,	    0,	    1],	    # HepB
    [0,	    0,	    0,	    0,	    1,	    1,	    0,	    0],	    # Hib
    [0,	    0,	    1,	    1,	    0,	    1,	    1,	    0],	    # IPV/OPV
    [-3,    0,	    0,	    0,	    1,	    0,	    0,	    0],	    # DTP Pent proportion
    [-4,    0,	    0,	    0,	    0,	    1,	    0,	    0],	    # DTP Hex proportion
    [-2,    0,	    0,	    0,	    0,	    0,	    1,	    0],	    # DTP DTP-IPV proportion
    [-2,    0,	    0,	    0,	    0,	    0,	    0,	    1],	    # DTP DTP-HepB proportion
    [0,	    -3,	    0,	    0,	    1,	    0,	    0,	    0],	    # HepB Pent proportion
    [0,	    0,	    -4, 	0,	    0,	    1,	    0,	    0]	    # IPV Hex proportion
])

df_vaccine_prices, df_vaccine_demand, df_vaccine_mfrs, df_vaccine_purchase = create_df_vaccine_prices()
# df_vaccine_prices:    
#   for each year and vaccine type, this array gives the price per dose, SUMMED over all manufacturers

# df_vaccine_demand: 
#   for each year and vaccine type, this array gives the TOTAL demand (annual # of doses) SUMMED over all manufacturers

# df_vaccine_mfrs:      
#   for each year and vaccine type, this array gives the total number of distinct products 
#   (i.e. made by distinct manufacturers)
#   the reason we do this by year is because we always consider the total # branded products by year.
#   (so even if SII produces for 5 years, the overlap won't affect our calculation since it isn't 
#   ever aggregated over all years)

# df_vaccine_purchase:
#   original dataframe filtered for our problem. we output it only to use for debugging.

# define an array to record historical demand for each product
hist_demand_by_vaccine = np.zeros((6, V)) # vaccines, years

# the following line doesn't do anything since it's already summed over manufacturers. 
# just delete it and replace it with the line below it to rename.
df_vaccine_demand_year_and_vaccine = df_vaccine_demand.groupby(level=['Year', 'Vaccine Type']).sum() # sum over mfrs
# this is data grouped by year and vaccine products where demand is a SUM of all reported demand for each entry
df_vaccine_demand_year_and_vaccine = df_vaccine_demand

for i, year in enumerate(['2015', '2016', '2017', '2018', '2019', '2020']): # for each year
    for j in range(V): # for each vaccine product
        # (total) historical demand by vaccine takes the total demand indexed by year i and vaccine type j
        hist_demand_by_vaccine[i][j] = df_vaccine_demand_year_and_vaccine.get((int(year), vaccine_names[j]), 0)

hist_demand = np.zeros((6, A)) # now by antigen
for i in range(A):
    for j in range(V):
        # historical demand by vaccine, filtering by whether antigen i is in vaccine type j
        # ith entry is a sum of demand per vaccine type j for all vaccine types j containing antigen i
        hist_demand[:,i] += vaccine_composition[i][j] * hist_demand_by_vaccine[:,j] / 10**6 # scale by 1 MIL
hist_demand = hist_demand.T # transpose for later calculations

#   2015                2016                2017                2018                2019                2020
#     [23.0927898*MIL,	263.219832*MIL,	    251.756335*MIL,	    201.515052*MIL,	    273.850309*MIL,	    279.148277*MIL],	# DTP
#     [21.5214628*MIL,	270.168934*MIL,	    291.04345*MIL,	    210.740201*MIL,	    242.110035*MIL,	    291.005583*MIL],	# HepB
#     [18.3257898*MIL,	254.348908*MIL,	    241.137705*MIL,	    190.919049*MIL,	    221.893716*MIL,	    227.138615*MIL],	# Hib
#     [82.4958*MIL,	    1237.315972*MIL,	1831.020034*MIL,	831.711148*MIL,	    1631.829657*MIL,	1070.478463*MIL]	# IPV/OPV
# ])

# create empty arrays:
avg_competing_price = np.zeros((6, V)) 
price_per_antigen = np.zeros((6, V))
sum_price_per_antigen_competing_products = np.zeros((6, V))
sum_competing_products = np.zeros((6, V))

# calculate price per antigen for all vaccine products
# the following line doesn't do anything since it's already summed over manufacturers. 
# just delete it and replace it with the line below it to rename.
df_vaccine_prices_year_and_vaccine = df_vaccine_prices.groupby(level=['Year', 'Vaccine Type']).sum() # sum over mfrs, just the same
# this is data grouped by year and vaccine products where prices are a SUM of all reported prices for each entry
df_vaccine_prices_year_and_vaccine = df_vaccine_prices 

for i, year in enumerate(['2015', '2016', '2017', '2018', '2019', '2020']): # for each year
    for j in range(V): # for each vaccine product
        # calculate price per antigen: price per product, year already summed over all manufacturers / number of antigens in product
        price_per_antigen[i][j] = df_vaccine_prices_year_and_vaccine.get((int(year), vaccine_names[j]), 0) / num_antigens[j]

# an array containing the total number of branded products for each year and vaccine product
total_branded_products = np.zeros((6, V)) 
for i, year in enumerate(['2015', '2016', '2017', '2018', '2019', '2020']): # for each year    
    for j in range(V):
        # only include vaccines produced in a given year in the list of competing products
        # basically just reformatting the data from df_vaccine_mfrs
        total_branded_products[i][j] = df_vaccine_mfrs.get((int(year), vaccine_names[j]), 0)


# calculate avg competing price for all vaccine products
for i, year in enumerate(['2015', '2016', '2017', '2018', '2019', '2020']): # for each year    
    for j in range(V): # for each vaccine product
        for c in range(V):  # enumerate through possible competitors
            sum_price_per_antigen_competing_products[i][j] += (
                vaccine_competition[j, c] *  # binary to filter out non-competing, and excluding self (see line 256-261)
                price_per_antigen[i, c]      # prices
            )
            sum_competing_products[i][j] += vaccine_competition_self[j, c] * total_branded_products[i, c]
        avg_competing_price[i][j] = num_antigens[j] * (
            price_per_antigen[i][j] # self
            + sum_price_per_antigen_competing_products[i][j] # excluding self
        ) / sum_competing_products[i][j] # divide by total number of competing products for year and vaccine
# num_antigens[v] * [
#     ( sum over mfr i: price[v,i,t] / num_antigens[v] ) +
#     ( sum over mfr i: price[v',i,t] / num_antigens[v'] )
# ] / competing_products[v]

# breakpoint()

# initial thresholds
profit_threshold = np.array([
    [252*MIL,   # AJ
    252*MIL,    # Beijing
    252*MIL,    # Bharat
    252*MIL,    # Bilthoven 
    252*MIL,    # Bio-Med
    330*MIL,    # Biologial E.
    252*MIL,    # Boryung
    252*MIL,    # Changchun
    252*MIL,    # GlaxoSmithKline
    252*MIL,    # Indian Immunologicals
    252*MIL,    # IVMB, Vietnam
    116*MIL,    # LG Chem
    229*MIL,    # Panacea
    252*MIL,    # POLYVAC
    252*MIL,    # PT Bio Farma
    252*MIL,    # Sanofi Healthcare
    252*MIL,    # Sanofi Pasteur
    322*MIL,    # SII
    252*MIL,    # Shantha
    252*MIL]    # VABIOTECH
])

# The specific column out of demand_projection is the same across its
# multi-values, so we just grab one value
demand_projection_single = demand_projection.values[0]

# total demand at t=0 for all the antigens -- times 2 for buffer
capacity = [np.sum(demand_projection_single[:,0])*2]* M
# estimate as 1/5 of capacity for all 5 antigens -- times 2 for buffer
hex_cap = np.divide(capacity, 5) * 2 

# upper limit for demand (hist)
upper_demand = np.array([
    279.148277,     # DTP
	291.005583,     # HepB
	1831.020034,    # IPV
    937.971518,     # OPV
	291.005583,     # Pent
	1831.020034,    # Hex
	1831.020034,    # DTP-IPV
	291.005583      # DTP-HepB
])


# ------------------ Adjustments for excluding mfrs, years, vaccines ------------------------------------

# remove excluded mfrs
M = M - len(excluded_mfrs)
mfr_index = list(range(1, M+1))       
mfr_resources = np.delete(mfr_resources, excluded_mfrs, axis=0)
mfr_resources2 = lambda_multi_param(
    lambda mfr_resources2_value: np.delete(mfr_resources2_value, excluded_mfrs, axis=0),
    mfr_resources2
)
profit_threshold = np.delete(profit_threshold, excluded_mfrs, axis=1)
hex_cost = lambda_multi_param(
    lambda hex_cost_value: np.delete(hex_cost_value, excluded_mfrs, axis=0),
    hex_cost
)

# remove excluded yrs
T = T - len(excluded_years) 
year_index = list(range(1, T+1))        
demand_projection = lambda_multi_param(
    lambda demand_projection_value: np.delete(demand_projection_value, excluded_years, axis=1),
    demand_projection
)

# remove excluded vaccines 
V = V - len(excluded_vaccines)
vaccine_index = list(range(1, V+1)) 
vaccine_names = [item for i, item in enumerate(vaccine_names) if i not in excluded_vaccines]
vaccine_composition = np.delete(vaccine_composition, excluded_vaccines, axis=1)
num_antigens = [item for i, item in enumerate(num_antigens) if i not in excluded_vaccines]
mfr_resources = np.delete(mfr_resources, excluded_vaccines, axis=1)
mfr_resources2 = lambda_multi_param(
    lambda mfr_resources2_value: np.delete(mfr_resources2_value, excluded_vaccines, axis=1),
    mfr_resources2
)
constraints = np.delete(constraints, excluded_vaccines, axis=1)

constraints_rows_to_remove = []
if 1 in excluded_vaccines: # if removing HepB
    constraints_rows_to_remove.append(8)
if 2 in excluded_vaccines or 5 in excluded_vaccines: # if removing IPV or Hex
    constraints_rows_to_remove.append(9) 

constraints = np.delete(constraints, constraints_rows_to_remove, axis=0)

avg_competing_price = np.delete(avg_competing_price, excluded_vaccines, axis=0)
upper_demand = np.delete(upper_demand, excluded_vaccines, axis=0)
historical_upper_price_limit = lambda_multi_param(
    lambda historical_upper_price_limit_value: np.delete(historical_upper_price_limit_value, excluded_vaccines, axis=0),
    historical_upper_price_limit
)


# ------------------ Calculations for demand curve coefficients ------------------------------------

mfr_products, num_mfrs = [], []
mfr_products = np.sum(mfr_resources, axis=1)      # vector of qty products by each mfr (sum rows)
num_mfrs = np.sum(mfr_resources, axis=0)          # vector of qty of vaccine products by mfr (sum cols)

num_constraints = np.shape(constraints)[0]       # count constraint rows
constraints_scaling = np.ones((num_constraints, V))
for i in range(4):
    constraints_scaling[i] = num_mfrs  

constraints = np.multiply(constraints, constraints_scaling)

profit_threshold = lambda_multi_param(
    lambda profit_scaling_factor_value: (profit_scaling_factor_value * profit_threshold/mfr_products).squeeze(),
    profit_scaling_factor
)

# demand constraint "b" vectors, RHS of Ax = b
constraints_demand = np.zeros((num_constraints, 6))     # hist years always 6
constraints_demand[0:A, 0:6] = hist_demand

# automate calculation of demand intercept a -- cols year, rows vax
demand_intercept = np.zeros((6, V))
demand_intercept = np.linalg.lstsq(constraints, constraints_demand, rcond=-1)[0]

# divide intercept by price
magnitude = np.divide(demand_intercept, avg_competing_price.T) # cols vaccines, rows years
# REMOVED negative
# negative_scale_b_c = [1]*V
# negative_scale = np.ones((magnitude.shape[0],magnitude.shape[1]))
# for i in range(magnitude.shape[0]):
#     if np.mean(magnitude, axis=1)[i] < 0:
#         negative_scale_b_c[i] = -1
#     for j in range(magnitude.shape[1]):
#         if magnitude[i,j] < 0:
#             negative_scale[i,j] = -1
# average scaling factor, then find order of magnitude difference
# scaling_b_c = np.floor(np.log10(np.absolute(np.mean(magnitude, axis=1)))) # avg over years magnitude diff between demand and price
magnitude = np.floor(np.log10(np.absolute(magnitude))) # magnitude diff between demand and price
#  [1. 0. 0. 1. 1. 0. 0. 0.]
bin_antigens = np.zeros((V,V))
for i in range(A):
    for j in range(V):
        if vaccine_composition[i,j] == 1: # if antigen i in vaccine j
            for k in range(V):
                if vaccine_composition[i,k] == 1:  # vaccine k also has i
                    bin_antigens[j,k] = 1

n_matrix = bin_antigens*num_mfrs

# n = np.zeros(6)
# for i in range(6):
#         n[i] = np.sum(total_branded_products[i]) # total number of branded products in year i

demand_coeff_a = np.zeros((6, V))
for i in range(6):
    for j in range(V):
        sf = 10**magnitude[j,i] # calculate scaling factor
        demand_coeff_a[i,j] = demand_intercept[j,i] + sf / (1 + (sum_competing_products[i,j]-1)*gamma) * avg_competing_price.T[j,i] # equation for demand coeff a

# updating scaling factors to be on order of demand coeff a
scaling_b_c = np.floor(np.log10(np.absolute(np.divide(demand_coeff_a, avg_competing_price))))

# demand coefficient a, averaged by year
demand_coeff_a = np.mean(demand_coeff_a, axis=0) # compressing to preserve cols (vaccine)

demand_coeff_b = np.zeros((6, V))
demand_coeff_c = np.zeros((6, V))

for i in range(6):
    for j in range(V):
        demand_coeff_b[i,j] = (10**scaling_b_c[i,j]) * (1+(sum_competing_products[i,j]-2)*gamma) / ((1+(sum_competing_products[i,j]-1)*gamma)*(1-gamma))  
        demand_coeff_c[i,j] = (10**scaling_b_c[i,j]) * gamma / ((1+(sum_competing_products[i,j]-1)*gamma)*(1-gamma))             

demand_coeff_b = np.mean(demand_coeff_b, axis=0) # compressing to preserve cols (vaccine)
demand_coeff_c = np.mean(demand_coeff_c, axis=0) # compressing to preserve cols (vaccine)

# if STANDARD == 1:

# orders of magnitude
mu3, mu2 = 1, 10 # may need to change ?
mu1 = 1
mu = [mu1, mu2, mu3]
dist_cost = 1 # distribution costs from COVID paper

# for naming conventions:
ys = np.array([2024, 2025, 2026, 2027, 2028, 2029, 2030])
ys = np.delete(ys, excluded_years)

vex = np.array(["DTP", "HepB", "IPV", "OPV", "Pent", "Hex", "DTP-IPV", "DTP-HepB"])
vex = vex[excluded_vaccines]
