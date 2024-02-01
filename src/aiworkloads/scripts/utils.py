import subprocess
import shutil
import os


def submit_job(cfg):
    if cfg.job_schedular.type == "slurm":
        # Full path to the SLURM job script
        full_script_path = f"{cfg.paths.generated_files}/slurm_job.sh"

        try:
            # Submit the job using sbatch
            subprocess.run(["sbatch", full_script_path], check=True)
            print(f"SLURM job submitted successfully using script: {full_script_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while submitting SLURM job: {e}")
    if cfg.job_schedular.type == "kubernetes":
        # TODO: implement kubernetes job submit implementation
        pass


def build_save_image(cfg):

    if cfg.containerization.type == "docker":
        tarball = f"{cfg.paths.generated_files}/{cfg.containerization.image_name}.tar"

        # Check if the tarball already exists
        if os.path.exists(tarball):
            print(
                f"Docker image tarball already exists at '{cfg.paths.generated_files}'. Skipping build and save."
            )
            return

        # copying selected workload
        # if "huggingface" in cfg.workload:
        src = os.path.join(os.getcwd(), "src/aiworkloads/workloads", cfg.workload.script)
        dest = os.path.join(cfg.paths.generated_files, cfg.workload.script)
        shutil.copyfile(src, dest)
        print(
            f"Copied workload script {cfg.workload.script} to {cfg.paths.generated_files}"
        )

        build_command = f"docker build -t {cfg.containerization.image_name} {cfg.paths.generated_files}"
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

        build_command = f"singularity build --fakeroot {cfg.containerization.image_name} docker:/{cfg.paths.generated_files}"
        try:
            subprocess.run(build_command, check=True, shell=True)
            print(
                f"Singularity image '{cfg.paths.generated_files}/{cfg.containerization.image_name}' built successfully."
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Singularity image: {e}")
