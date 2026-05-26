# gavi.mod

# ----- SETS ------------------
set VACCINES := 1..9;   # vaccines: 1 DTP 2 HepB 3 Hib 4 IPV 5 Pent 6 Hex 7 OPV 8 DTaP-IPV 9 DTwP-HepB
set ANTIGENS := 1..5;   # antigens: 1 DTP 2 HepB 3 Hib 4 IPV 5 OPV
#set COMPET{ANTIGENS};   # vaccines containing antigen a
#set COMPOSITION{VACCINES};  # antigens making up each vaccine v
param M >= 0;           # number of manufacturers
set MFRS := 1..M;       # manufacturers
param T >= 0;           # length of tender/time horizon
set HORIZON := 1..T;    # time horizon

# ------ PARAMETERS -------------
param mu1 >= 0;  # objective function weights
param mu2 >= 0;
param mu3 >= 0;

# param a{VACCINES, HORIZON} >= 0;  # demand curve constants
param a{VACCINES} >= 0;
param b >= 0;
param c >= 0;
param d;  # rate of (linear) distribution cost
# param n{VACCINES} >= 0;

param profit{MFRS} >= 0;  # required profit
param capacity{MFRS} >= 0;  # capacity for existing vaccines
param hexCost{MFRS} >= 0;  # cost of developing hexavalent vaccine
param hexCapacity{MFRS} >= 0;  # capacity for hexavalent vaccine

param demand{ANTIGENS, HORIZON};  # demand

param composition{ANTIGENS, VACCINES} binary; # binary matrix relating antigens and vaccines

param num{VACCINES};  # number of antigens in each vaccine

# ---- DECISION VARIABLES -------------
var price{v in VACCINES, MFRS, HORIZON} >= 0;  # price
var quant{v in VACCINES, MFRS, HORIZON} >= 0;  # quantity

var y{MFRS} binary;  # whether mfr i should produce the hexavalent vaccine
var z >= 0;  # bound on price difference

# ------ OBJECTIVE FUNCTION --------
minimize WeightedObj:
    sum{i in MFRS, t in HORIZON} (mu1 * sum{v in VACCINES}((price[v,i,t] + d) * quant[v,i,t]) - mu2*quant[6,i,t]) + mu3 * z;
    # change 7 to 6

# ----- CONSTRAINTS ----------------

# Define z, the maximum difference in mfr prices for each year and vaccine
subject to DefineZ{i in MFRS, j in MFRS, t in HORIZON, v in VACCINES: i<>j}:
    z >= price[v,i,t] - price[v,j,t];

# Condition on objective function weights
subject to ObjectiveFuncWeights:
    mu1 + mu2 + mu3 = 1;

# Ensure total demand is met
subject to DemandConstraint{n in ANTIGENS, t in HORIZON}:
    sum{i in MFRS, v in VACCINES} (quant[v,i,t])*composition[n,v] >= demand[n,t];

# Only have a contracted hexavalent quantity if mfr invests in the production capacity to develop it
subject to HexProductionCapacity1{i in MFRS, t in HORIZON}:
    quant[6,i,t] <= hexCapacity[i] * y[i];

# Only have a contracted hexavalent price if mfr invests in the production capacity to develop it
subject to HexProductionCapacity2{i in MFRS, t in HORIZON}:
    price[6,i,t] <= hexCapacity[i] * y[i];

# Production capacity limit on existing vaccines
subject to ProductionCapacity{i in MFRS, t in HORIZON}:
    sum{v in VACCINES: v <> 6}(quant[v,i,t]) <= capacity[i];

# Ensure manufacturers make at least minimum profit P
subject to ProfitThreshold{i in MFRS}:
    sum{t in HORIZON, v in VACCINES}(quant[v,i,t]*price[v,i,t]) >= T*profit[i] + hexCost[i]*y[i];

# # Quantities follow linear demand curve
# subject to LinearDemand{i in MFRS, v in VACCINES, t in HORIZON}:
#   quant[v,i,t] + b*price[v,i,t] - c*(sum{j in MFRS, n in ANTIGENS, v2 in COMPET[n]: j<>i}(price[v2,j,t]))
#   = sum{n in ANTIGENS, v2 in COMPET[n]}(a[v2,t]);

# Quantities follow linear demand curve
# subject to LinearDemand{i in MFRS, v in VACCINES, t in HORIZON}:
  # quant[v,i,t] + b*price[v,i,t] - c*(sum{j in MFRS, n in ANTIGENS, v2 in COMPET[n]: j<>i}(price[v2,j,t]))
  # = sum{n in ANTIGENS, v2 in COMPET[n]}(a[v2]);

# updated ver
subject to LinearDemandCurve{i in MFRS, v in VACCINES, t in HORIZON}:
    quant[v,i,t] + (b*price[v,i,t])/num[v] - c*((sum{j in MFRS: j<>i}(price[v,j,t]/num[v]))
    + (sum{n in ANTIGENS, j in MFRS, v2 in VACCINES: v2<>v}(composition[n,v])*(price[v2,j,t]/num[v2])*composition[n,v2])) = a[v]; # check notation?
