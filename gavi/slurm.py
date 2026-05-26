import logging
from fabric import Connection

# relative to home
RUNS_DIR = "gavi_runs"

class SlurmConnection():
    def __init__(self, slurm_ssh_login, slurm_account, slurm_email, verbose=False):
        self.conn = Connection(slurm_ssh_login)
        self.slurm_account = slurm_account
        self.slurm_email = slurm_email
        self.verbose = verbose

    def create_slurm_script(self, trial_name):
        return (
            "#!/bin/bash\n"
            f"#SBATCH --job-name=gavi_trial_{trial_name}\n"
            f"#SBATCH --account={self.slurm_account}\n"
            "#SBATCH --partition=tier3\n" # debug, change to tier3 when looks good

            # output
            f"#SBATCH --output=slurm_output_%j\n"
            f"#SBATCH --error=slurm_error_%j\n"
            f"#SBATCH --mail-user={self.slurm_email}\n"
            "#SBATCH --mail-type=END\n"

            # resource usage
            "#SBATCH --time=0-17:00:00\n" # max runtime of 17h 
            "#SBATCH --cpus-per-task=8\n" # 16 > 12
            "#SBATCH --mem-per-cpu=10g\n"
            "#SBATCH --requeue\n"

            # "PreemptMode=Suspend,Gang\n" 
            # "PreemptType=preempt/partition_prio\n"

            # code to get it to not cancel...
            # "trap 'scontrol requeue ${SLURM_JOB_ID}; exit 15' 15\n"
            # "wait\n"
            # "#SBATCH --oversubscribe=NO\n"

            # run ampl
            "#SBATCH --licenses=ampl:1\n"
            "module load ampl\n"
            "module load gurobi\n"
            "srun ampl_runner\n"
        )

    def submit_job(self, mod_text, dat_text, commands_text, trial_name, debug_text):
        self.conn.run(f"mkdir -p {RUNS_DIR}/{trial_name}")
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/debug\n"
            f"{debug_text}\n"
            "EOF"
        )
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/ampl_model\n"
            f"{mod_text}\n"
            "EOF"
        )
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/ampl_data\n"
            f"{dat_text}\n"
            "EOF"
        )
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/ampl_commands\n"
            f"{commands_text}\n"
            "EOF"
        )
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/ampl_script\n"
            "model ampl_model;\n"
            "data ampl_data;\n"
            "include ampl_commands;\n"
            "EOF"
        )
        self.conn.run(
            f"cat <<'EOF' > {RUNS_DIR}/{trial_name}/ampl_runner\n"
            "#!/bin/bash\n"
            "ampl ampl_script\n"
            "RESULT=$?\n"
            "if [ $RESULT -eq 0 ]; then\n"
            "  echo Job succeeded\n"
            "else\n"
            "  sleep 60\n"
            "  JOB_ID=$(cat slurm_job_id)\n"
            "  echo Requeuing job $JOB_ID\n"
            "  scontrol requeue $JOB_ID\n"
            "fi\n"
            "EOF"
        )
        self.conn.run(f"chmod +x {RUNS_DIR}/{trial_name}/ampl_runner")
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/slurm_script\n"
            f"{self.create_slurm_script(trial_name)}\n"
            "EOF"
        )
        result = self.conn.run(f"sbatch --chdir={RUNS_DIR}/{trial_name} {RUNS_DIR}/{trial_name}/slurm_script")
        self.job_id = result.stdout.strip().split()[3]
        self.conn.run(
            f"cat <<EOF > {RUNS_DIR}/{trial_name}/slurm_job_id\n"
            f"{self.job_id}\n"
            "EOF"
        )
        if self.verbose:
            logging.info(f"Submitted Slurm job: {self.job_id}")
