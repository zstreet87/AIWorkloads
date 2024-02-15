import os


def generate_job_schedular_script(cfg):
    env_vars = ""
    if cfg.model_framework.env_vars:
        for key, value in cfg.model_framework.env_vars.items():
            env_vars += f"export {key}='{value}'\n"

    # TODO: module loads in slurm config to add
    module_loads = ""

    # TODO: perhaps a better abstraction would get rid of this ugliness
    model_framework_cmd = ""
    if cfg.model_framework.type == "huggingface" or cfg.model_framework.type == "example":
        model_framework_cmd = f"{cfg.model_framework.cmd} {cfg.paths.cache}/{cfg.model_framework.runner}"
    if cfg.model_framework.type == "superbench":
        model_framework_cmd = (
            f"{cfg.model_framework.cmd} --config-file {cfg.model_framework.superbench_config}"
        )

    job_schedular_script = ""
    if cfg.job_schedular.type == "slurm":
        job_schedular_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={cfg.job_schedular.job_name}
#SBATCH --output=job.%j.out 
#SBATCH --partition={cfg.job_schedular.partition}
#SBATCH --nodes={cfg.job_schedular.nodes} 
#SBATCH --ntasks={cfg.job_schedular.ntasks}         # should be total number of gpus
#SBATCH --time={cfg.job_schedular.time}             # total run time limit (HH:MM:SS)

export MASTER_PORT=$(expr 10000 + $(echo -n $SLURM_JOBID | tail -c 4))
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export GPUS_PER_NODE=$(echo "$SLURM_TASKS_PER_NODE" | grep -o '[0-9]*' | head -n 1)
export WORLD_SIZE=$(($SLURM_NNODES * $GPUS_PER_NODE))
export LOCAL_RANK=$SLURM_LOCALID
export RANK=$SLURM_PROCID

{env_vars}
{module_loads}

srun singularity exec -B \
{cfg.paths.work}:{cfg.paths.work} \
{cfg.containerization.prefix}{cfg.paths.work}/{cfg.containerization.image_name}{cfg.containerization.suffix} \
{model_framework_cmd}
        """

    if cfg.job_schedular.type == "kubernetes":
        # TODO: Need to implement the kubernetes-job-schedular-script generation
        pass

    script_path = os.path.join(cfg.paths.cache, "job_schedular.sh")
    with open(script_path, "w") as file:
        file.write(job_schedular_script)
    print(f"Job-schedular script generated at {script_path}")
