import hydra
from omegaconf import DictConfig, OmegaConf
import os
import sys

from singularity import build_and_save_image

# Add the project root to the Python path in one line
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegen import generate_workload_script, generate_dockerfile, generate_slurm_script


# Adding the scripts directory to the Python path
# scripts_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(scripts_dir)

# Import other scripts from the scripts folder if needed
# from other_script import some_function


@hydra.main(version_base=None, config_path="../", config_name="config")
def main(cfg: DictConfig):

    generate_workload_script(cfg.workload)
    generate_dockerfile(cfg.dockerfile)

    image_name = "my_docker_image"
    build_and_save_image(".", image_name)

    generate_slurm_script(cfg.slurm, cfg.workload, image_name)


if __name__ == "__main__":
    main()
