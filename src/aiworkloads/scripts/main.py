import hydra
from omegaconf import DictConfig

from aiworkloads.codegen import (
    generate_model_framework_script,
    generate_dockerfile,
    generate_job_schedular_script,
)

from aiworkloads.scripts.utils import (
    setup_paths,
    copy_model_framework_to_path,
    build_save_image,
    submit_job,
)


@hydra.main(version_base=None, config_path="../configs", config_name="config")
def main(cfg: DictConfig) -> None:

    setup_paths(cfg)

    if cfg.workflow.setup_model_framework:
        generate_model_framework_script(cfg)
        copy_model_framework_to_path(cfg)
    if cfg.workflow.setup_image:
        generate_dockerfile(cfg)
        build_save_image(cfg)
    if cfg.workflow.setup_job_schedular:
        generate_job_schedular_script(cfg)
    if cfg.workflow.submit_job:
        submit_job(cfg)


if __name__ == "__main__":
    main()
