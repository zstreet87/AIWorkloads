import os


def generate_workload_script(cfg):
    workload_script = ""
    # NOTE: only supporting hf script generation at the moment
    if cfg.workload.type == "huggingface":
        workload_script = f"""#!/usr/bin/env bash
# HF script
python {cfg.workload.script} \\
    --model_name {cfg.workload.model_name} \\
    --task {cfg.workload.task} \\
    --dataset {cfg.workload.training.dataset} \\
    --dataset_config {cfg.workload.training.dataset_config} \\
    --batch_size {cfg.workload.batch_size} \\
    --num_epochs {cfg.workload.num_epochs} \\
    --learning_rate {cfg.workload.training.learning_rate} \\
    --model_save_path {cfg.paths.generated_files} \\
    --results_save_path {cfg.paths.generated_files} \\
    {cfg.workload.additional_args}
        """

    script_path = os.path.join(cfg.paths.generated_files, "workload.sh")
    with open(script_path, "w") as file:
        file.write(workload_script)
    print(f"AI workload script generated at {script_path}")
