import os


def generate_workload_script(cfg):
    workload_script = ""
    # NOTE: only supporting hf script generation at the moment
    if cfg.workload.use_huggingface:
        workload_script = f"""#!/usr/bin/env bash
# HF script
python {cfg.workload.huggingface.script} \\
    --model_name {cfg.workload.huggingface.model_name} \\
    --task {cfg.workload.huggingface.task} \\
    --dataset {cfg.workload.huggingface.training.dataset} \\
    --dataset_config {cfg.workload.huggingface.training.dataset_config} \\
    --batch_size {cfg.workload.common.batch_size} \\
    --num_epochs {cfg.workload.common.num_epochs} \\
    --learning_rate {cfg.workload.huggingface.training.learning_rate} \\
    --model_save_path {cfg.paths.generated_files} \\
    --results_save_path {cfg.paths.generated_files} \\
    {cfg.workload.huggingface.additional_args}
        """

    script_path = os.path.join(cfg.paths.generated_files, "workload.sh")
    with open(script_path, "w") as file:
        file.write(workload_script)
    print(f"AI workload script generated at {script_path}")
