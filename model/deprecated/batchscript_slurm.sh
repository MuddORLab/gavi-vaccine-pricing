#!/bin/bash

# Set the SLURM parameters
#SBATCH --job-name=AMPL-batch
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err 
#SBATCH --mem-per-cpu=100
#SBATCH --cpus-per-task=16
#SBATCH --time=20:00:00
#SBATCH --mail-user=<zmeznarich@hmc.edu>
#SBATCH --account=hexavalent
#SBATCH -p debug

# Load the AMPL module
module load ampl
echo "Hello 1!"

# # Set the path to the AMPL executable
# AMPL=/path/to/ampl

# Set the path to the directory containing the dat files
DAT_DIR=/home/zxmeie/gavi_runs/april

# Set the parameters to vary
historical_upper_price_limit=(
    {0.45, 1.81, 4.73, 2.06, 2.65, 207, 17.7, 2.3}
)
historical_upper_price_limit_5=()
historical_upper_price_limit_10=()

for price in "${historical_upper_price_limit[@]}"; do
    historical_upper_price_limit_5+=($(echo "$price*5" | bc -l))
    historical_upper_price_limit_10+=($(echo "$price*10" | bc -l))
done
historical_upper_price_limit_COMBINED=("${historical_upper_price_limit[@]}" "${historical_upper_price_limit_5[@]}" "${historical_upper_price_limit_10[@]}")
echo "Hello 2!"

DEMAND_PROJ=(
    "196.577949    200.295609     203.776515     207.197014     210.249261     213.249984     216.196634;
    220.726573    224.846562     228.913068     232.857313     236.405680     239.868796     243.251377;
    190.504523    194.244332     197.777238     201.155884     204.226794     207.232195     210.188594;
    391.456441    401.202911     408.983746     117.911386     120.180762     122.415286     124.566235"
    "196.577949    200.295609     203.776515     207.197014     210.249261     213.249984     216.196634;
    220.726573    224.846562     228.913068     232.857313     236.405680     239.868796     243.251377;
    190.504523    194.244332     197.777238     201.155884     204.226794     207.232195     210.188594;
    391.456441    401.202911     408.983746     416.7890637	    424.5783354	    432.4347005	   440.311319"
) # original, extrapolated
echo "Hello 2.1!"

PROFIT=(
    {252, 252, 252, 252, 252, 330, 252, 252, 252, 252, 252, 116, 229, 252, 252, 252, 252, 322, 252, 252}
)
PROFIT_10DOWN=()
PROFIT_10UP=()

for profit in "${PROFIT[@]}"; do
    PROFIT_10DOWN+=($(echo "$profit*0.9" | bc -l))
    PROFIT_10UP+=($(echo "$profit*1.1" | bc -l))
done
PROFIT_COMBINED=("${PROFIT[@]}" "${PROFIT_10DOWN[@]}" "${PROFIT_10UP[@]}")
echo "Hello 2.2!"

HP=(0.01 0.05 0.1)
echo "Hello 2.3!"
OPV=(0.333 0.667 1)
echo "Hello 2.4!"

# Loop over the parameter combinations and dat files and submit a job for each one
for upperPrice in "${historical_upper_price_limit[@]}"; do
    for demand in "${DEMAND_PROJ[@]}"; do
        for profit in "${PROFIT_COMBINED[@]}"; do
            for hexProportion in "${HP[@]}"; do
                for opvFrac in "${OPV[@]}"; do
                    for dat_file in $DAT_DIR/*.dat; do
                        # Extract the file name without the extension
                        dat_name=$(basename "$dat_file" .dat)
                        echo "Hello 2.5!"

                        # Create the SLURM submission script
                        cat << EOF > "${dat_name}_${upperPrice[0]}_${demand[0]}_${profit[0]}_${hexProportion}_${opvFrac}.job"
echo "Hello 3!"

#SBATCH --job-name=${dat_name}_${upperPrice[0]}_${demand[0]}_${profit[0]}_${hexProportion}_${opvFrac}

echo "Hello 4!"

module load ampl

$AMPL "hex.mod" "${dat_name}.dat" upperPrice="${upperPrice//;/ }" demand="${demand//;/ }" profit="${profit//;/ }" $hexProportion $opvFrac
echo "Hello 5!"
EOF

            # Submit the job to SLURM
            sbatch "${dat_name}_${upperPrice[0]}_${demand[0]}_${profit[0]}_${hexProportion}_${opvFrac}.job"
            echo "Hello 6!"
        done
    done
done
