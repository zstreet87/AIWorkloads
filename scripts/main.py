import hydra
from omegaconf import DictConfig
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegen import (
    generate_workload_script,
    generate_dockerfile,
    generate_job_schedular_script,
)

from utils import build_save_image, submit_job


@hydra.main(version_base=None, config_path="../", config_name="config")
def main(cfg: DictConfig):

    generate_workload_script(cfg)
    generate_dockerfile(cfg)
    build_save_image(cfg)
    generate_job_schedular_script(cfg)
    submit_job(cfg)


if __name__ == "__main__":
    main()
