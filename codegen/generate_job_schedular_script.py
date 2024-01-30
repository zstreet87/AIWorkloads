import os


def generate_job_schedular_script(cfg):

    env_vars_script = ""

    # Function to add environment variables
    def add_env_vars(env_vars):
        nonlocal env_vars_script
        for key, value in env_vars.items():
            env_vars_script += f"export {key}='{value}'\n"

    if cfg.job_schedular.use_slurm:
        # Check for Hugging Face environment variables
        if cfg.workload.use_huggingface and "env_vars" in cfg.workload.huggingface:
            add_env_vars(cfg.workload.huggingface.env_vars)

        # Check for DeepSpeed environment variables
        if cfg.workload.use_deepspeed and "env_vars" in cfg.workload.deepspeed:
            add_env_vars(cfg.workload.deepspeed.env_vars)

        launch_container = ""
        if cfg.containerization.use_docker:
            launch_container = (
                f'docker-archive://"$WORK"/{cfg.containerization.docker.image_name}'
            )
        if cfg.containerization.use_singularity:
            launch_container = f'"$WORK"/{cfg.containerization.singularity.image_name}'

        slurm_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={cfg.job_schedular.slurm.job_name}
#SBATCH --output=job.%j.out 
#SBATCH --partition={cfg.job_schedular.slurm.partition}
#SBATCH --nodes={cfg.job_schedular.slurm.nodes} 
#SBATCH --ntasks={cfg.job_schedular.slurm.ntasks}         # should be total number of gpus
#SBATCH --time={cfg.job_schedular.slurm.time}             # total run time limit (HH:MM:SS)

# Environment variable exports
{env_vars_script}

module load singularity  # Load Singularity module using LMod
srun singularity exec \\
    -B {cfg.paths.generated_files}:{cfg.paths.generated_files} \\ # mounting shared-file system
    {launch_container}
        """

        script_path = os.path.join(cfg.paths.generated_files, "slurm_job.sh")
        with open(script_path, "w") as file:
            file.write(slurm_script)
        print(f"Slurm script generated at {script_path}")

    if cfg.job_schedular.use_kubernetes:
        # TODO: Need to implement the kubernetes-job-schedular-script generation
        pass
