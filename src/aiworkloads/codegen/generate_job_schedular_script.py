from pathlib import Path
from string import Template


def generate_job_schedular_script(cfg):
    def generate_env_vars(env_vars):
        return "\n".join(f"export {key}='{value}'" for key, value in env_vars.items())

    def generate_huggingface_cmd(cfg):
        return (
            f"{cfg.model_framework.cmd} {cfg.paths.cache}/{cfg.model_framework.runner}"
        )

    def generate_superbench_cmd(cfg):
        return f"{cfg.model_framework.cmd} --config-file {cfg.model_framework.superbench_config}"

    model_framework_cmd_map = {
        "huggingface": generate_huggingface_cmd,
        "example": generate_huggingface_cmd,  # Assuming 'example' uses the same command format
        "superbench": generate_superbench_cmd,
        # Add other model frameworks here as needed
    }

    if cfg.model_framework.type not in model_framework_cmd_map:
        raise ValueError(
            f"Unsupported model framework type: {cfg.model_framework.type}"
        )

    model_framework_cmd = model_framework_cmd_map[cfg.model_framework.type](cfg)

    def generate_slurm_script(cfg, env_vars, module_loads, model_framework_cmd):
        slurm_template = Template(
            """#!/usr/bin/env bash
#SBATCH --job-name=$job_name
#SBATCH --output=job.%j.out
#SBATCH --partition=$partition
#SBATCH --nodes=$nodes
#SBATCH --ntasks=$ntasks
#SBATCH --time=$time

export MASTER_PORT=$(expr 10000 + $(echo -n $SLURM_JOBID | tail -c 4))
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export GPUS_PER_NODE=$(echo "$SLURM_TASKS_PER_NODE" | grep -o '[0-9]*' | head -n 1)
export WORLD_SIZE=$(($SLURM_NNODES * $GPUS_PER_NODE))
export LOCAL_RANK=$SLURM_LOCALID
export RANK=$SLURM_PROCID

$env_vars
$module_loads

srun singularity exec -B $work_dir:$work_dir \\
${container_prefix}${work_dir}/${container_image}${container_suffix} \\
$model_framework_cmd
"""
        )
        return slurm_template.substitute(
            job_name=cfg.job_schedular.job_name,
            partition=cfg.job_schedular.partition,
            nodes=cfg.job_schedular.nodes,
            ntasks=cfg.job_schedular.ntasks,
            time=cfg.job_schedular.time,
            env_vars=env_vars,
            module_loads=module_loads,
            work_dir=cfg.paths.work,
            container_prefix=cfg.containerization.prefix,
            container_image=cfg.containerization.image_name,
            container_suffix=cfg.containerization.suffix,
            model_framework_cmd=model_framework_cmd,
        )

    def generate_k8_script(cfg):
        for container in cfg.spec.containers:
            cfg.job_schedular.spec[container].args = cfg.model_framework.runner
        return f"#!/usr/bin/env bash\nkubectl create -f {cfg.job_schedular}\n"

    job_scheduler_script_map = {
        "slurm": generate_slurm_script,
        "k8": generate_k8_script,
        # Add other job schedulers here as needed
    }

    if cfg.job_schedular.type not in job_scheduler_script_map:
        raise ValueError(f"Unsupported job scheduler type: {cfg.job_schedular.type}")

    env_vars = (
        generate_env_vars(cfg.model_framework.env_vars)
        if cfg.model_framework.env_vars
        else ""
    )
    module_loads = ""  # To be implemented if needed

    if cfg.job_schedular.type == "slurm":
        job_schedular_script = job_scheduler_script_map["slurm"](
            cfg, env_vars, module_loads, model_framework_cmd
        )
    else:
        job_schedular_script = job_scheduler_script_map[cfg.job_schedular.type](cfg)

    script_path = Path(cfg.paths.cache) / "job_schedular.sh"
    script_path.write_text(job_schedular_script)
    print(f"Job-schedular script generated at {script_path}")
