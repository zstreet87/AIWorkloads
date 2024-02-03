import hydra
from omegaconf import DictConfig

from aiworkloads.codegen import (
    generate_workload_script,
    generate_dockerfile,
    generate_job_schedular_script,
)

from aiworkloads.scripts.utils import (
    setup_paths,
    copy_workload_to_path,
    build_save_image,
    submit_job,
)


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def main(cfg: DictConfig) -> None:

    setup_paths(cfg)
    generate_workload_script(cfg)
    copy_workload_to_path(cfg)
    generate_dockerfile(cfg)
    build_save_image(cfg)
    generate_job_schedular_script(cfg)
    submit_job(cfg)


if __name__ == "__main__":
    main()
