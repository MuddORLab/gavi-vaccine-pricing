# noHex.mod

# ----- SETS ------------------ ** ordered = same spot otherwise need change
set VACCINES ordered;   # vaccines: 1 DTP 2 HepB 3 IPV 4 OPV 5 Pent 6 DTaP-IPV 7 DTwP-HepB
set ANTIGENS ordered;   # antigens: 1 DTP 2 HepB 3 Hib 4 Polio
param M >= 0;           # number of manufacturers
set MFRS := 1..M;       # manufacturers
param T >= 0;           # length of tender/time horizon
set HORIZON := 1..T;    # time horizon

# ------ PARAMETERS -------------
param mu1 >= 0;  # objective function weights
param mu2 >= 0;
param mu3 >= 0;

param a{VACCINES} >= 0; # demand curve coeff
param b{VACCINES} >= 0;
param c{VACCINES} >= 0;
param d;  # rate of (linear) distribution cost
param N; 	# 1000
param N1; 	# million
param N2;	# 100
# param n{VACCINES} >= 0;

param profit{MFRS} >= 0;  # required profit
param capacity{MFRS} >= 0;  # capacity for existing vaccines
# no hexCost
# no hexCapacity

param demand{ANTIGENS, HORIZON};  # demand
param upperDemand{VACCINES};      # upper limit on demand
param upperPrice{VACCINES};       # upper limit on price

param composition{ANTIGENS, VACCINES} binary; # binary matrix relating antigens and vaccines
param resources{MFRS, VACCINES} binary; # resources by mfr to produce vax v

param num{VACCINES};  # number of antigens in each vaccine

# no hexProportion

# ---- DECISION VARIABLES -------------
var price{v in VACCINES, MFRS, HORIZON} >= 0;  # price
var quant{v in VACCINES, i in MFRS, t in HORIZON} := max{n in ANTIGENS}(demand[n,t]*composition[n,v]
                                            /sum{j in MFRS, v2 in VACCINES}(resources[j,v2]*composition[n,v2])),
                                             >= 0;  # quantity

# no y
var z >= 0;  # bound on price difference

var x{v in VACCINES, i in MFRS, t in HORIZON} := resources[i,v], binary;     # if vaccine v is produced in year t

# ------ OBJECTIVE FUNCTION --------
minimize WeightedObj:
    sum{i in MFRS, t in HORIZON} (mu1 * sum{v in VACCINES}((price[v,i,t] + d) * quant[v,i,t])) # quant lower for hex (1/6) 
    - mu2 * sum{v in VACCINES, i in MFRS, t in HORIZON} (x[v,i,t]) # sum over all vaccine products
    + mu3 * z;

# ----- CONSTRAINTS ----------------
# Define z, the maximum difference in mfr prices for each year and vaccine
subject to DefineZ{i in MFRS, j in MFRS, t in HORIZON, v in VACCINES: i<>j}:
    z >= price[v,i,t] - price[v,j,t] - (upperPrice[v] * (1-x[v,i,t])) - (upperPrice[v] * (1-x[v,j,t]));

# Ensure total demand is met
subject to DemandConstraint{n in ANTIGENS, t in HORIZON}:
    sum{i in MFRS, v in VACCINES} (quant[v,i,t]*composition[n,v]) >= demand[n,t];   # change back capacity

# no HexProductionCapacity1

# no HexProductionCapacity 2

# Production capacity limit on existing vaccines
subject to ProductionCapacity{i in MFRS, t in HORIZON}:
    sum{v in VACCINES} (quant[v,i,t]) <= capacity[i];

# Ensure manufacturers make at least minimum profit P
subject to ProfitThreshold{i in MFRS}:
    sum{t in HORIZON, v in VACCINES}(quant[v,i,t]*price[v,i,t]) >= profit[i]*sum{t in HORIZON, v in VACCINES}(x[v,i,t]);

# Zero quantity forces binary 0
subject to ZeroQuantity{i in MFRS, v in VACCINES, t in HORIZON}:
    x[v,i,t] <= N1*quant[v,i,t];

# Zero price forces binary 0
subject to ZeroPrice{i in MFRS, v in VACCINES, t in HORIZON}:
    x[v,i,t] <= N2*price[v,i,t];

# Nonzero quantity forces binary 1 (not for hex because we want mfr to be able to start produce)
subject to NonzeroQuantity{i in MFRS, v in VACCINES, t in HORIZON}:
    upperDemand[v]*x[v,i,t]*resources[i,v] >= quant[v,i,t];

# no NonzeroQuantityHex

# Nonzero price forces binary 1 (not for hex because we want mfr to be able to start produce)
subject to NonzeroPrice{i in MFRS, v in VACCINES, t in HORIZON}:
    upperPrice[v]*x[v,i,t]*resources[i,v] >= price[v,i,t]; 

# no NonzeroPriceHex

# Linear demand curve relaxation (only when quantity > 0)
subject to NonzeroLinearDemandCurveGEQ{i in MFRS, v in VACCINES, t in HORIZON}:
    quant[v,i,t]
    + (b[v]*price[v,i,t])/num[v]
    - c[v]*(
        (sum{j in MFRS: j<>i} (price[v,j,t]/num[v])) 
        + (
            sum{n in ANTIGENS, j in MFRS, v2 in VACCINES: v2<>v}
            (composition[n,v])
            *(price[v2,j,t]/num[v2])
            *composition[n,v2]
        )
    )
    >= a[v] - (upperDemand[v] * (1-x[v,i,t]));

subject to NonzeroLinearDemandCurveLEQ{i in MFRS, v in VACCINES, t in HORIZON}:
    quant[v,i,t]
    + (b[v]*price[v,i,t])/num[v]
    - c[v]*(
        (sum{j in MFRS: j<>i} (price[v,j,t]/num[v])) 
        + (
            sum{n in ANTIGENS, j in MFRS, v2 in VACCINES: v2<>v}
            (composition[n,v])
            *(price[v2,j,t]/num[v2])
            *composition[n,v2]
        )
    )
    <= a[v] + (upperDemand[v] * (1-x[v,i,t]));

# Quantity of OPV cannot exceed 2/3 of projected polio demand (2 of three PV doses)
subject to OPVLimit{t in HORIZON}:
    sum{i in MFRS}(quant[member(4, VACCINES),i,t]) <= (2/3)*(demand[member(4, ANTIGENS),t]); 

# no HexThreshold

# Manufacturer must produce at least 1 (million)
subject to MinimumQty{i in MFRS, v in VACCINES, t in HORIZON}:
	quant[v,i,t] >= x[v,i,t];

# no CostMargin constraints since no Hexavalent vaccine in model
