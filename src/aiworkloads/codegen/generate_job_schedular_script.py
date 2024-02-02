import os


def generate_job_schedular_script(cfg):

    env_vars = ""
    if cfg.workload.env_vars:
        for key, value in cfg.workloads.env_vars.items():
            env_vars += f"export {key}='{value}'\n"

    end_cmd = ""
    if cfg.workload.type == "huggingface":
        end_cmd = f"{cfg.workload.script}"
    if cfg.workload.type == "superbench":
        end_cmd = f"--config-file {cfg.workload}"

    if cfg.job_schedular.type == "slurm":

        slurm_script = f"""#!/usr/bin/env bash
#SBATCH --job-name={cfg.job_schedular.job_name}
#SBATCH --output=job.%j.out 
#SBATCH --partition={cfg.job_schedular.partition}
#SBATCH --nodes={cfg.job_schedular.nodes} 
#SBATCH --ntasks={cfg.job_schedular.ntasks}         # should be total number of gpus
#SBATCH --time={cfg.job_schedular.time}             # total run time limit (HH:MM:SS)

export MASTER_PORT=$(expr 10000 + $(echo -n $SLURM_JOBID | tail -c 4))
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export GPUS_PER_NODE=$(echo "$SLURM_GPUS_ON_NODE" | grep -o '[0-9]*' | head -n 1)
export WORLD_SIZE=$(($SLURM_NNODES * $GPUS_PER_NODE))
export LOCAL_RANK=$SLURM_LOCALID
export RANK=$SLURM_PROCID

echo "***SLURM Launch Info***"
echo "MASTER_PORT="$MASTER_PORT
echo "MASTER_ADDR="$MASTER_ADDR
echo "WORLD_SIZE="$WORLD_SIZE
echo "GPUS_PER_NODE="$GPUS_PER_NODE
echo "LOCAL_RANK="$LOCAL_RANK
echo "RANK="$RANK
echo "***********************"

# Environment variable exports
{env_vars}

module load singularity  # Load Singularity module using LMod
srun singularity exec \\
    -B {cfg.paths.shared_file_system}:{cfg.paths.shared_file_system} \\ # mounting shared-file system
    {cfg.containerization.prefix}{cfg.paths.shared_file_system}/{cfg.containerization.image_name} {cfg.workload.cmd} {end_cmd}
        """

        script_path = os.path.join(cfg.paths.shared_file_system, "slurm_job.sh")
        with open(script_path, "w") as file:
            file.write(slurm_script)
        print(f"Slurm script generated at {script_path}")

    if cfg.job_schedular.type == "kubernetes":
        # TODO: Need to implement the kubernetes-job-schedular-script generation
        pass
