import os

def generate_slurm_script(slurm_cfg):
    slurm_script = f"""#!/bin/bash
#SBATCH --job-name={slurm_cfg.job_name}
#SBATCH --cpus-per-task={slurm_cfg.cpus_per_task}
#SBATCH --mem-per-cpu={slurm_cfg.mem_per_cpu}
#SBATCH --time={slurm_cfg.time}

# Add your Slurm job commands here
"""

    script_path = os.path.join(os.getcwd(), "slurm_job.sh")
    with open(script_path, "w") as file:
        file.write(slurm_script)
    print(f"Slurm script generated at {script_path}")
