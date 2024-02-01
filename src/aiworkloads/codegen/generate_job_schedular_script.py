import os


def generate_job_schedular_script(cfg):

    env_vars = ""

    def add_env_vars(vars):
        nonlocal env_vars
        for key, value in vars.items():
            env_vars += f"export {key}='{value}'\n"

    if cfg.workload.env_vars:
        add_env_vars(cfg.workload.env_vars)

    if cfg.job_schedular.type == "slurm":

        launch_container = ""
        if cfg.containerization.type == "docker":
            launch_container = (
                f'docker-archive://"$WORK"/{cfg.containerization.image_name}'
            )
        if cfg.containerization.type == "singularity":
            launch_container = f'"$WORK"/{cfg.containerization.image_name}'

        slurm_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={cfg.job_schedular.job_name}
#SBATCH --output=job.%j.out 
#SBATCH --partition={cfg.job_schedular.partition}
#SBATCH --nodes={cfg.job_schedular.nodes} 
#SBATCH --ntasks={cfg.job_schedular.ntasks}         # should be total number of gpus
#SBATCH --time={cfg.job_schedular.time}             # total run time limit (HH:MM:SS)

# Environment variable exports
{env_vars}

module load singularity  # Load Singularity module using LMod
srun singularity exec \\
    -B {cfg.paths.generated_files}:{cfg.paths.generated_files} \\ # mounting shared-file system
    {launch_container}
        """

        script_path = os.path.join(cfg.paths.generated_files, "slurm_job.sh")
        with open(script_path, "w") as file:
            file.write(slurm_script)
        print(f"Slurm script generated at {script_path}")

    if cfg.job_schedular.type == "kubernetes":
        # TODO: Need to implement the kubernetes-job-schedular-script generation
        pass
