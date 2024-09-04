from pathlib import Path
from string import Template


def generate_model_framework_script(cfg):
    def generate_scheduler_env_setup(cfg):
        scheduler_env_map = {
            "slurm": Template(
                """# SLURM environment variables setup
export SLURM_PROCID=${SLURM_PROCID:-0}
export WORLD_SIZE=${WORLD_SIZE:-1}
export GPUS_PER_NODE=${GPUS_PER_NODE:-1}
"""
            ).substitute(
                SLURM_PROCID=cfg.job_scheduler.slurm.env_vars.SLURM_PROCID,
                WORLD_SIZE=cfg.job_scheduler.slurm.env_vars.WORLD_SIZE,
                GPUS_PER_NODE=cfg.job_scheduler.slurm.env_vars.GPUS_PER_NODE,
            ),
            "k8": Template(
                """# Kubernetes environment variables setup
export K8_NODE_RANK=${K8_NODE_RANK:-0}
export K8_NUM_NODES=${K8_NUM_NODES:-1}
"""
            ).substitute(
                K8_NODE_RANK=cfg.job_scheduler.k8.env_vars.K8_NODE_RANK,
                K8_NUM_NODES=cfg.job_scheduler.k8.env_vars.K8_NUM_NODES,
            ),
            # Add other job scheduler setups here as needed
        }

        return scheduler_env_map.get(cfg.job_scheduler.type, "")

    def generate_install_requirements(cfg):
        """
        Generates the pip install command for required dependencies.
        """
        if cfg.model_framework.requirements:
            requirements_list = " ".join(cfg.model_framework.requirements)
            return f"pip install {requirements_list}\n"
        return ""

    def generate_huggingface_script(cfg):
        scheduler_env_setup = generate_scheduler_env_setup(cfg)
        install_requirements = generate_install_requirements(cfg)

        hf_template = Template(
            """#!/usr/bin/env bash
# HF script
${scheduler_env_setup}
${install_requirements}
python ${script_path} \\
    --model_name ${model_name} \\
    --task ${task} \\
    --dataset_name ${dataset_name} \\
    --dataset_config_name ${dataset_config_name} \\
    --batch_size ${batch_size} \\
    --num_epochs ${num_epochs} \\
    --learning_rate ${learning_rate} \\
    --model_save_path ${model_save_path} \\
    --results_save_path ${results_save_path} \\
    ${additional_args}
"""
        )
        return hf_template.substitute(
            scheduler_env_setup=scheduler_env_setup,
            install_requirements=install_requirements,
            script_path=f"{cfg.paths.cache}/{cfg.model_framework.script}",
            model_name=cfg.model_framework.model_name,
            task=cfg.model_framework.task,
            dataset_name=cfg.model_framework.training.dataset,
            dataset_config_name=cfg.model_framework.training.dataset_config,
            batch_size=cfg.model_framework.batch_size,
            num_epochs=cfg.model_framework.num_epochs,
            learning_rate=cfg.model_framework.training.learning_rate,
            model_save_path=cfg.paths.work,
            results_save_path=cfg.paths.cwd,
            additional_args=cfg.model_framework.additional_args,
        )

    def generate_example_script(cfg):
        example_template = Template(
            """#!/usr/bin/env bash
# Example script
python ${script_path}
"""
        )
        return example_template.substitute(
            script_path=f"{cfg.paths.cache}/{cfg.model_framework.script}"
        )

    model_framework_script_map = {
        "huggingface": generate_huggingface_script,
        "example": generate_example_script,
        # Add other model frameworks here as needed
    }

    if cfg.model_framework.type not in model_framework_script_map:
        raise ValueError(
            f"Unsupported model framework type: {cfg.model_framework.type}"
        )

    model_framework_script = model_framework_script_map[cfg.model_framework.type](cfg)

    script_path = Path(cfg.paths.cache) / "model_framework.sh"
    script_path.write_text(model_framework_script)
    print(f"Model framework script generated at {script_path}")
