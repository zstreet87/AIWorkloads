import subprocess
from pathlib import Path
import shutil
from string import Template


def setup_paths(cfg):
    """Sets up necessary paths for caching and working directories."""
    cache_folder = Path.home() / ".cache" / "aiworkloads"
    cache_folder.mkdir(parents=True, exist_ok=True)
    cfg.paths.cache = str(cache_folder)
    cfg.paths.cwd = str(Path.cwd())


def run_command(command, success_msg, error_msg):
    """Runs a shell command and handles success and error messages."""
    try:
        subprocess.run(command, check=True, shell=True)
        print(success_msg)
    except subprocess.CalledProcessError as e:
        print(f"{error_msg}: {e}")


def submit_job(cfg):
    """Submits the job using the appropriate scheduler command."""
    full_script_path = Path(cfg.paths.cache) / "job_schedular.sh"

    cmd_map = {"slurm": "sbatch", "bash": "bash"}  # Default or fallback

    cmd = cmd_map.get(cfg.job_schedular.type, "bash")
    run_command(
        f"{cmd} {full_script_path}",
        success_msg=f"Job submitted successfully using script: {full_script_path}",
        error_msg="Error occurred while submitting job",
    )


def copy_model_framework_to_path(cfg):
    """Copies the model framework script to the cache path."""
    if cfg.model_framework.script:
        src = (
            Path.home()
            / "AIWorkloads"
            / "src"
            / "aiworkloads"
            / "model_framework"
            / cfg.model_framework.script
        )
        dest = Path(cfg.paths.cache) / cfg.model_framework.script
        shutil.copyfile(src, dest)
        print(
            f"Copied model_framework script {cfg.model_framework.script} to {cfg.paths.cache}"
        )


def build_save_image(cfg):
    """Builds and saves a Docker or Singularity image based on the configuration."""

    container_actions = {
        "docker": lambda: docker_actions(cfg),
        "singularity": lambda: singularity_actions(cfg),
    }

    action = container_actions.get(cfg.containerization.type)
    if action:
        action()


def docker_actions(cfg):
    """Handles Docker-specific build and save actions."""
    tarball_path = Path(cfg.paths.work) / f"{cfg.containerization.image_name}.tar"

    if tarball_path.exists():
        print(
            f"Docker image tarball already exists at '{tarball_path}'. Not using generated Dockerfile, skipping build and save."
        )
        return

    build_template = Template("docker build -t ${image_name} ${work_path}")
    build_command = build_template.substitute(
        image_name=cfg.containerization.image_name, work_path=cfg.paths.work
    )

    run_command(
        build_command,
        success_msg=f"Docker image '{cfg.containerization.image_name}' built successfully.",
        error_msg="Error occurred while building Docker image",
    )

    save_template = Template("docker save -o ${tarball_path} ${image_name}")
    save_command = save_template.substitute(
        tarball_path=tarball_path, image_name=cfg.containerization.image_name
    )

    run_command(
        save_command,
        success_msg=f"Docker image saved as tarball at '{tarball_path}'.",
        error_msg="Error occurred while saving Docker image as tarball",
    )


def singularity_actions(cfg):
    """Handles Singularity-specific build actions."""
    sif_path = Path(cfg.paths.work) / cfg.containerization.image_name

    if sif_path.exists():
        print(
            f"Singularity image already exists at '{sif_path}'. Not using generated Dockerfile, skipping build and save."
        )
        return

    build_template = Template(
        "singularity build --fakeroot ${sif_path} docker://${docker_image}"
    )
    build_command = build_template.substitute(
        sif_path=sif_path, docker_image=cfg.paths.docker_image
    )

    run_command(
        build_command,
        success_msg=f"Singularity image '{sif_path}' built successfully.",
        error_msg="Error occurred while building Singularity image",
    )
