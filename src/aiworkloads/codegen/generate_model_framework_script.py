import os


def generate_workload_script(cfg):
    model_framework_script = ""
    # NOTE: only supporting hf script generation at the moment
    if cfg.model_framework.type == "huggingface":
        model_framework_script = f"""#!/usr/bin/env bash
# HF script
python {cfg.paths.cache}/{cfg.model_framework.script} \\
    --model_name {cfg.model_framework.model_name} \\
    --task {cfg.model_framework.task} \\
    --dataset_name {cfg.model_framework.training.dataset} \\
    --dataset_config_name {cfg.model_framework.training.dataset_config} \\
    --batch_size {cfg.model_framework.batch_size} \\
    --num_epochs {cfg.model_framework.num_epochs} \\
    --learning_rate {cfg.model_framework.training.learning_rate} \\
    --model_save_path {cfg.paths.work} \\
    --results_save_path {cfg.paths.cwd} \\
    {cfg.model_framework.additional_args}
        """

    if cfg.model_framework.type == "superbench":
        # TODO: Implement superbench model_framework script generation
        pass

    if cfg.model_framework.type == "example":
        model_framework_script = f"""#!/usr/bin/env bash
# example script
python {cfg.paths.cache}/{cfg.model_framework.script}
        """

    script_path = os.path.join(cfg.paths.cache, "model_framework.sh")
    with open(script_path, "w") as file:
        file.write(model_framework_script)
    print(f"Model framework script generated at {script_path}")
