import hydra
from omegaconf import DictConfig, OmegaConf
import os
import sys

# Add the project root to the Python path in one line
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codegen import generate_slurm_script, generate_workload_script


# Adding the scripts directory to the Python path
# scripts_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(scripts_dir)

# Import other scripts from the scripts folder if needed
# from other_script import some_function


@hydra.main(version_base=None, config_path="../", config_name="config")
def main(cfg: DictConfig):
    # Generate Slurm script
    generate_slurm_script(cfg.slurm)

    # Generate AI workload script
    generate_workload_script(cfg.ai_workload)


if __name__ == "__main__":
    main()
