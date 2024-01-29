import os


def generate_workload_script(workload_cfg):
    workload_script = ""
    if workload_cfg.use_huggingface:
        # Hugging Face specific setup
        hf_cfg = workload_cfg.huggingface
        workload_script = f"""#!/usr/bin/env bash
        # HF script
        python {hf_cfg.script_path} \\
            --model_name {hf_cfg.model_name} \\
            --task {hf_cfg.task} \\
            --dataset {hf_cfg.training.dataset} \\
            --dataset_config {hf_cfg.training.dataset_config} \\
            --batch_size {workload_cfg.common.batch_size} \\
            --num_epochs {workload_cfg.common.num_epochs} \\
            --learning_rate {hf_cfg.training.learning_rate} \\
            --model_save_path {hf_cfg.output.model_save_path} \\
            --results_save_path {hf_cfg.output.results_save_path} \\
            {hf_cfg.additional_args}
        """

    script_path = os.path.join(os.getcwd(), "workload.sh")
    with open(script_path, "w") as file:
        file.write(workload_script)
    print(f"AI workload script generated at {script_path}")
