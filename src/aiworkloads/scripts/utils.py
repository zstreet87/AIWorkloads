import subprocess
from pathlib import Path
import shutil


def setup_paths(cfg):
    cache_folder = Path.home() / ".cache" / "aiworkloads"
    cache_folder.mkdir(parents=True, exist_ok=True)
    cfg.paths.cache = str(cache_folder)
    cfg.paths.cwd = str(Path.cwd())


def submit_job(cfg):
    full_script_path = Path(cfg.paths.cache) / "job_schedular.sh"
    cmd = "sbatch" if cfg.job_schedular.type == "slurm" else "bash"
    try:
        subprocess.run([cmd, full_script_path], check=True)
        print(f"job submitted successfully using script: {full_script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while submitting job: {e}")


def copy_model_framework_to_path(cfg):
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
    if cfg.containerization.type == "docker":
        tarball_path = Path(cfg.paths.work) / f"{cfg.containerization.image_name}.tar"

        # Check if the tarball already exists
        if tarball_path.exists():
            print(
                f"Docker image tarball already exists at '{tarball_path}'. Not using generated Dockerfile, skipping build and save."
            )
            return

        build_command = (
            f"docker build -t {cfg.containerization.image_name} {cfg.paths.work}"
        )
        try:
            subprocess.run(build_command, check=True, shell=True)
            print(
                f"Docker image '{cfg.containerization.image_name}' built successfully."
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Docker image: {e}")
            return  # Exit if build fails

        save_command = (
            f"docker save -o {tarball_path} {cfg.containerization.image_name}"
        )
        try:
            subprocess.run(save_command, check=True, shell=True)
            print(f"Docker image saved as tarball at '{tarball_path}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while saving Docker image as tarball: {e}")

    if cfg.containerization.type == "singularity":
        sif_path = Path(cfg.paths.work) / cfg.containerization.image_name
        if sif_path.exists():
            print(
                f"Singularity image already exists at '{sif_path}'. Not using generated Dockerfile, skipping build and save."
            )
            return

        # Note: Adjust the Docker image source format as needed
        build_command = (
            f"singularity build --fakeroot {sif_path} docker://{cfg.paths.docker_image}"
        )
        try:
            subprocess.run(build_command, check=True, shell=True)
            print(f"Singularity image '{sif_path}' built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Singularity image: {e}")
