import subprocess
from pathlib import Path
import shutil
import os


def setup_paths(cfg):
    cache_folder = Path.home() / ".cache" / "aiworkloads"
    cache_folder.mkdir(parents=True, exist_ok=True)
    cfg.paths.cache = str(cache_folder)
    cfg.paths.cwd = str(Path.cwd())


def submit_job(cfg):
    if cfg.job_schedular.type == "slurm":
        full_script_path = f"{cfg.paths.cache}/job_schedular.sh"

        try:
            subprocess.run(["sbatch", full_script_path], check=True)
            print(f"SLURM job submitted successfully using script: {full_script_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while submitting SLURM job: {e}")
    if cfg.job_schedular.type == "kubernetes":
        # TODO: implement kubernetes job submit implementation
        pass


def copy_model_framework_to_path(cfg):
    if cfg.model_framework.script:
        src = os.path.join(
            Path.home(), "AIWorkloads/src/aiworkloads/model_framework", cfg.model_framework.script
        )
        dest = os.path.join(cfg.paths.cache, cfg.model_framework.script)
        shutil.copyfile(src, dest)
        print(f"Copied model_framework script {cfg.model_framework.script} to {cfg.paths.cache}")


def build_save_image(cfg):

    if cfg.containerization.type == "docker":
        tarball = f"{cfg.paths.work}/{cfg.containerization.image_name}.tar"

        # Check if the tarball already exists
        if os.path.exists(tarball):
            print(
                f"Docker image tarball already exists at '{cfg.paths.work}'. Not using generated Dockerfile, skipping build and save."
            )
            return

        build_command = (
            f"docker build -t {cfg.containerization.image_name} {cfg.paths.work}"
        )
        try:
            subprocess.run(build_command, check=True, shell=True)
            print(f"Docker image '{tarball}' built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Docker image: {e}")
            return  # Exit if build fails

        save_command = f"docker save -o {tarball} {cfg.containerization.image_name}"
        try:
            subprocess.run(save_command, check=True, shell=True)
            print(f"Docker image saved as tarball at '{tarball}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while saving Docker image as tarball: {e}")

    if cfg.containerization.type == "singularity":

        sif = f"{cfg.paths.work}/{cfg.containerization.image_name}.sif"

        # Check if the tarball already exists
        if os.path.exists(sif):
            print(
                f"Singularity image already exists at '{cfg.paths.work}'. Not using generated Dockerfile, skipping build and save."
            )
            return
        build_command = f"singularity build --fakeroot {cfg.containerization.image_name} docker:/{cfg.paths.work}"
        try:
            subprocess.run(build_command, check=True, shell=True)
            print(
                f"Singularity image '{cfg.paths.work}/{cfg.containerization.image_name}' built successfully."
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Singularity image: {e}")
