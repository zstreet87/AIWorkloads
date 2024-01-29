import os


def generate_slurm_script(slurm_cfg, workload_cfg, image_name):

    env_vars_script = ""

    # Function to add environment variables
    def add_env_vars(env_vars):
        nonlocal env_vars_script
        for key, value in env_vars.items():
            env_vars_script += f"export {key}='{value}'\n"

    # Check for Hugging Face environment variables
    if workload_cfg.use_huggingface and "env_vars" in workload_cfg.huggingface:
        add_env_vars(workload_cfg.huggingface.env_vars)

    # Check for DeepSpeed environment variables
    if workload_cfg.use_deepspeed and "env_vars" in workload_cfg.deepspeed:
        add_env_vars(workload_cfg.deepspeed.env_vars)

    slurm_script = f"""#!/usr/bin/env bash
        #SBATCH --job-name={slurm_cfg.job_name}
        #SBATCH --output=job.%j.out 
        #SBATCH --partition={slurm_cfg.partition}
        #SBATCH --nodes={slurm_cfg.nodes} 
        #SBATCH --ntasks={slurm_cfg.ntasks}         # should be total number of gpus
        #SBATCH --time={slurm_cfg.time}             # total run time limit (HH:MM:SS)

        # Environment variable exports
        {env_vars_script}

        module load singularity  # Load Singularity module using LMod
        singularity exec \
        -B $WORK:$WORK \
        docker-archive://$WORK/{image_name}\n")
    """

    script_path = os.path.join(os.getcwd(), "slurm_job.sh")
    with open(script_path, "w") as file:
        file.write(slurm_script)
    print(f"Slurm script generated at {script_path}")
