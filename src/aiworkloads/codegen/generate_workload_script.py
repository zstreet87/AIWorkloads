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
    --model_save_path {cfg.paths.shared_file_system} \\
    --results_save_path {cfg.paths.shared_file_system} \\
    {cfg.workload.additional_args}
        """
    if cfg.workload.type == "superbench":
        # TODO: Implement superbench workload script generation
        pass

    script_path = os.path.join(cfg.paths.shared_file_system, "workload.sh")
    with open(script_path, "w") as file:
        file.write(workload_script)
    print(f"AI workload script generated at {script_path}")
