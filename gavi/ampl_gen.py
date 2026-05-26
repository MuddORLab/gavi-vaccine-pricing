from .trials import TrialParams

def construct_table_row_numbered(n):
    return " ".join(str(i+1) for i in range(n))

def construct_table_row(xs):
    return " ".join(str(x) for x in xs)

# Generate the text of the dat file for a trial
# Trial is a row of the params dataframe
def create_dat_text(trial: TrialParams):
    # write header
    text = "# hex.dat\n\n"

    # write sets
    text += f"set VACCINES := {construct_table_row(trial.vaccine_names)};\n"
    text += f"set ANTIGENS := {construct_table_row(trial.antigen_names)};\n\n"

    # write set params
    text += f"param M := {trial.M};\n"
    text += f"param T := {trial.T};\n\n"
    
    if 5 not in trial.excluded_vaccines:
        text += f"param hexProportion := {trial.hex_proportion};\n\n"

    # write out obj function weight mu1, mu2, mu3
    for m in range(len(trial.mu)):
        text += f"param mu{m+1} := {trial.mu[m]};\n"
    text += "\n"

    # write opvFrac
    text += f"param opvFrac := {trial.opv_frac};\n\n"

    # write out a, b, and c for linear demand constraint
    text += "param a :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.demand_coeff_a[i]}"
    text += ";\n"
    text += "param b :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.demand_coeff_b[i]}"
    text += ";\n"
    text += "param c :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.demand_coeff_c[i]}"
    text += ";\n"
    # write out d for rate of (linear) distribution cost
    text += f"param d := {trial.dist_cost};\n\n"
    text += f"param N := {trial.N};\n"
    text += f"param N1 := {trial.N1};\n"
    text += f"param N2 := {trial.N2};\n"

    # write out profit, capacity (if not hex)
    if 5 in trial.excluded_vaccines:
        text += "param: profit\t\tcapacity :="
        for i in range(trial.M):
            text += (
                f"\n{i+1}"
                f"\t\t{trial.profit_threshold[i]}"
                f"\t\t{trial.capacity[i]}"
            )
        text += " ;\n"
        
    # write out profit, capacity, cost, and Q
    else:
        text += "param: profit\t\tcapacity\t\thexCost\t\thexCapacity :="
        for i in range(trial.M):
            text += (
                f"\n{i+1}"
                f"\t\t{trial.profit_threshold[i]}"
                f"\t\t{trial.capacity[i]}"
                f"\t\t{trial.hex_cost[i]}"
                f"\t\t{trial.hex_cap[i]}"
            )
        text += " ;\n"

    # write out demand
    text += f"param demand : {construct_table_row(trial.year_index)} :="
    for i, antigen in enumerate(trial.antigen_names):
        text += f"\n\t{antigen}\t{construct_table_row(trial.demand_projection[i])}"
    text += ";\n"

    # write out upperDemand
    text += "param upperDemand :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.upper_demand[i]}"
    text += ";\n"

    # write out upperPrice
    text += "param upperPrice :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.historical_upper_price_limit[i]}"
    text += ";\n"

    # write out composition
    text += f"param composition : {construct_table_row(trial.vaccine_names)} :="
    for i, antigen in enumerate(trial.antigen_names):
        text += f"\n\t{antigen}\t{construct_table_row(trial.vaccine_composition[i])}"
    text += ";\n"

    # write out resources
    text += f"param resources : {construct_table_row(trial.vaccine_names)} :="
    for i, mfr in enumerate(trial.mfr_index):
        text += f"\n\t{mfr}\t{construct_table_row(trial.mfr_resources[i])}"
    text += ";\n"

    # write out resources2
    text += f"param resources2 : {construct_table_row(trial.vaccine_names)} :="
    for i, mfr in enumerate(trial.mfr_index):
        text += f"\n\t{mfr}\t{construct_table_row(trial.mfr_resources2[i])}"
    text += ";\n"

    # write out num
    text += "param num :="
    for i, vaccine in enumerate(trial.vaccine_names):
        text += f"\n\t{vaccine}\t{trial.num_antigens[i]}"
    text += ";\n"

    return text
