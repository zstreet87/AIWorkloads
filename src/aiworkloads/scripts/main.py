import argparse
import hydra
from hydra import initialize, compose
from omegaconf import DictConfig
import pkg_resources
import os
import sys

from aiworkloads.codegen import (
    generate_workload_script,
    generate_dockerfile,
    generate_job_schedular_script,
)

from aiworkloads.scripts.utils import build_save_image, submit_job


# @hydra.main(version_base=None, config_path="../../configs", config_name="config")
# def main(cfg: DictConfig):
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", help="Path to the user configuration file", required=True
    )
    args = parser.parse_args()

    # # Initialize Hydra with default configs
    initialize(config_path="../../configs", job_name="aiworkloads")

    cfg = compose(config_name="config")
    # cfg = compose(
    #     config_name="config", overrides=[f"user_config={args.config}"]
    # )
    print(cfg)
    #
    # generate_workload_script(cfg)
    # generate_dockerfile(cfg)
    # build_save_image(cfg)
    # generate_job_schedular_script(cfg)
    # submit_job(cfg)


if __name__ == "__main__":
    main()
