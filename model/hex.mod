# hex.mod (with combined Polio antigen)

# ––––––––––––––––– SETS ––––––––––––––––– ** ordered = same spot otherwise need change
set VACCINES ordered;   # vaccines: 1 DTP 2 HepB 3 IPV 4 OPV 5 Pent 6 Hex 7 DTaP-IPV 8 DTwP-HepB
set ANTIGENS ordered;   # antigens: 1 DTP 2 HepB 3 Hib 4 Polio
param M >= 0;           # number of manufacturers
set MFRS := 1..M;       # manufacturers
param T >= 0;           # length of tender/time horizon
set HORIZON := 1..T;    # time horizon

# ––––––––––––––––– PARAMETERS –––––––––––––––––
param mu1 >= 0;  # objective function weights
param mu2 >= 0;
param mu3 >= 0;

param opvFrac >= 0; # fraction of demand to OPV

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
param hexCost{MFRS} >= 0;  # cost of developing hexavalent vaccine
param hexCapacity{MFRS} >= 0;  # capacity for hexavalent vaccine

param demand{ANTIGENS, HORIZON};  # demand
param upperDemand{VACCINES};      # upper limit on demand
param upperPrice{VACCINES};       # upper limit on price

param composition{ANTIGENS, VACCINES} binary; # binary matrix relating antigens and vaccines
param resources{MFRS, VACCINES} binary; # historical resources by mfr to produce vaccine v
param resources2{MFRS, VACCINES} binary; # projected/assumed resources by mfr to produce vaccine v

param num{VACCINES};  # number of antigens in each vaccine

param hexProportion >= 0;   # % of demand per antigen met by hexavalent

param upperQuant{v in VACCINES, t in HORIZON} := min(max{n in ANTIGENS}(demand[n,t]*composition[n,v]), upperDemand[v]);

param initQuant{v in VACCINES, i in MFRS, t in HORIZON} := min(max{n in ANTIGENS}(demand[n,t]*composition[n,v]*resources[i,v]
                                          /sum{j in MFRS, v2 in VACCINES}(resources[j,v2]*composition[n,v2])), upperDemand[v]);


# ––––––––––––––––– DECISION VARIABLES –––––––––––––––––
var price{v in VACCINES, MFRS, HORIZON} >= 0;  # price
var quant{v in VACCINES, i in MFRS, t in HORIZON} := initQuant[v,i,t], <= upperQuant[v,t], >= 0;  # quantity

var w{v in VACCINES, i in MFRS, t in HORIZON} >= 0; # McCormick linearization variable
var x{v in VACCINES, i in MFRS, t in HORIZON} := resources[i,v], <= resources2[i,v], binary;     # if vaccine v is produced in year t
var y{i in MFRS} := resources[i,member(6, VACCINES)], <= resources2[i,member(6, VACCINES)], binary;  # whether mfr i should produce the hexavalent vaccine
var z >= 0;  # bound on price difference


# ––––––––––––––––– OBJECTIVE FUNCTION –––––––––––––––––
minimize WeightedObj:
    sum{i in MFRS, t in HORIZON} (mu1 * sum{v in VACCINES}((w[v,i,t] + d * quant[v,i,t]))) # quant lower for hex (1/6) 
    - mu2 * sum{v in VACCINES, i in MFRS, t in HORIZON} (x[v,i,t]) # sum over all vaccine products
    + mu3 * z;

# ––––––––––––––––– CONSTRAINTS –––––––––––––––––
# 1 – McCormick linearization constraints –––
subject to Mc1{v in VACCINES, i in MFRS, t in HORIZON}: 
    w[v,i,t] >= upperQuant[v,t] * price[v,i,t] 
    + quant[v,i,t] * upperPrice[v] 
    - upperQuant[v,t]*upperPrice[v];

subject to Mc2{v in VACCINES, i in MFRS, t in HORIZON}: 
    w[v,i,t] <= upperQuant[v,t]*price[v,i,t];

subject to Mc3{v in VACCINES, i in MFRS, t in HORIZON}:
    w[v,i,t] <= quant[v,i,t]*upperPrice[v];

# 2 – Define z, the maximum difference in mfr prices for each year and vaccine
subject to DefineZ{i in MFRS, j in MFRS, t in HORIZON, v in VACCINES: i<>j}:
    z >= price[v,i,t] - price[v,j,t] - (upperPrice[v] * (1-x[v,i,t])) - (upperPrice[v] * (1-x[v,j,t]));

# 3 – Ensure total demand is met
subject to DemandConstraint{n in ANTIGENS, t in HORIZON}:
    sum{i in MFRS, v in VACCINES} (quant[v,i,t]*composition[n,v]) >= demand[n,t];   # change back capacity

# 4 – Only have a contracted hexavalent quantity if mfr invests in the production capacity to develop it
subject to HexProductionCapacity1{i in MFRS, t in HORIZON}:
    quant[member(6, VACCINES),i,t] <= hexCapacity[i] * y[i]; 

# 5 – Only have a contracted hexavalent price if mfr invests in the production capacity to develop it
subject to HexProductionCapacity2{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] <= hexCapacity[i] * y[i];

# 6 – Production capacity limit on existing vaccines
subject to ProductionCapacity{i in MFRS, t in HORIZON}:
    sum{v in VACCINES: v <> member(6, VACCINES)}(quant[v,i,t]) <= capacity[i]; 

# 7 – Ensure manufacturers make at least minimum profit P (and make up for hex cost)
subject to ProfitThreshold{i in MFRS}:
    sum{t in HORIZON, v in VACCINES}(w[v,i,t]) >= profit[i]*sum{t in HORIZON, v in VACCINES}(x[v,i,t]) + hexCost[i]*y[i];

# DUMMY: Quant = 0
# subject to DUMMY{i in MFRS, t in HORIZON, v in VACCINES: v <> member(6, VACCINES)}:
# 	quant[v,i,t] = 0;

# 8 – Zero quantity forces binary 0
subject to ZeroQuantity{i in MFRS, v in VACCINES, t in HORIZON}:
    x[v,i,t] <= quant[v,i,t]; # removed scaling factors RHS for numerical stability

# 9 – Zero price forces binary 0
subject to ZeroPrice{i in MFRS, v in VACCINES, t in HORIZON}:
    x[v,i,t] <= N2*price[v,i,t]; 

# 10 – Nonzero quantity forces binary 1
subject to NonzeroQuantity{i in MFRS, v in VACCINES, t in HORIZON}:
    upperDemand[v]*x[v,i,t] >= quant[v,i,t];

# 11 – Nonzero price forces binary 1
subject to NonzeroPrice{i in MFRS, v in VACCINES, t in HORIZON}:
    upperPrice[v]*x[v,i,t] >= price[v,i,t]; 
  
# 12 – Linear demand curve relaxation (only when quantity > 0)
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

# 13 – Linear demand curve relaxation (only when quantity > 0)
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

# 14 – Quantity of OPV cannot exceed fraction of projected polio demand (i.e. 2 of three PV doses)
subject to OPVLimit{t in HORIZON}:
    sum{i in MFRS}(quant[member(4, VACCINES),i,t]) <= (opvFrac)*(demand[member(4, ANTIGENS),t]); 

# 15 – Certain percentage of antigen demand must be met by Hexavalent vaccine
subject to HexThreshold{n in ANTIGENS, t in HORIZON}:
    sum{i in MFRS}(quant[member(6, VACCINES),i,t]) >= hexProportion * demand[n,t];

# 16 – Manufacturer must produce at least 1 (million)
subject to MinimumQty{i in MFRS, v in VACCINES, t in HORIZON}:
	quant[v,i,t] >= x[v,i,t];

# 17 – Price should be at least 1 penny
subject to MinimumPrice{i in MFRS, v in VACCINES, t in HORIZON}:
	price[v,i,t] >= 0.01*x[v,i,t];

# 18 – Cost Hex >= sum of all possible parts –––
# Cost Hex >= Pent + IPV
subject to CostMargin53{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(5, VACCINES),i,t] + price[member(3, VACCINES),i,t] 
                                    - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= Pent + OPV
subject to CostMargin54{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(5, VACCINES),i,t] + price[member(4, VACCINES),i,t] 
                                    - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= DTP + HepB + IPV
subject to CostMargin123{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(1, VACCINES),i,t] + price[member(2, VACCINES),i,t] 
                                    + price[member(3, VACCINES),i,t] - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= DTP + HepB + OPV
subject to CostMargin124{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(1, VACCINES),i,t] + price[member(2, VACCINES),i,t] 
                                    + price[member(4, VACCINES),i,t] - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= HepB + DTP-IPV
subject to CostMargin27{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(2, VACCINES),i,t] + price[member(7, VACCINES),i,t] 
                                    - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= IPV + DTP-HepB
subject to CostMargin38{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(3, VACCINES),i,t] + price[member(8, VACCINES),i,t] 
                                    - N*(1-x[member(6, VACCINES),i,t]);

# Cost Hex >= OPV + DTP-HepB
subject to CostMargin48{i in MFRS, t in HORIZON}:
    price[member(6, VACCINES),i,t] >= price[member(4, VACCINES),i,t] + price[member(8, VACCINES),i,t] 
                                    - N*(1-x[member(6, VACCINES),i,t]);
