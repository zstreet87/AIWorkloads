import subprocess
import shutil
import os


def submit_job(cfg):
    if cfg.job_schedular.use_slurm:
        # Full path to the SLURM job script
        full_script_path = f"{cfg.paths.generated_files}/slurm_job.sh"

        try:
            # Submit the job using sbatch
            subprocess.run(["sbatch", full_script_path], check=True)
            print(f"SLURM job submitted successfully using script: {full_script_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while submitting SLURM job: {e}")
    if cfg.job_schedular.use_kubernetes:
        # TODO: implement kubernetes job submit implementation
        pass


def build_save_image(cfg):

    if cfg.containerization.use_docker:
        tarball = (
            f"{cfg.paths.generated_files}/{cfg.containerization.docker.image_name}.tar"
        )

        # Check if the tarball already exists
        if os.path.exists(tarball):
            print(
                f"Docker image tarball already exists at '{cfg.paths.generated_files}'. Skipping build and save."
            )
            return

        # copying selected workload
        if cfg.workload.use_huggingface:
            src = os.path.join(
                os.getcwd(), "workloads", cfg.workload.huggingface.script
            )
            dest = os.path.join(
                cfg.paths.generated_files, cfg.workload.huggingface.script
            )
            shutil.copyfile(src, dest)
            print(
                f"Copied workload script {cfg.workload.huggingface.script} to {cfg.paths.generated_files}"
            )

        build_command = f"docker build -t {cfg.containerization.docker.image_name} {cfg.paths.generated_files}"
        try:
            # Execute the Singularity build command
            subprocess.run(build_command, check=True, shell=True)
            print(f"Docker image '{tarball}' built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Docker image: {e}")
            return  # Exit if build fails

        # Save the Docker image as a tarball
        save_command = (
            f"docker save -o {tarball} {cfg.containerization.docker.image_name}"
        )
        try:
            subprocess.run(save_command, check=True, shell=True)
            print(f"Docker image saved as tarball at '{tarball}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while saving Docker image as tarball: {e}")

    if cfg.containerization.use_singularity:
        # # Get the path from the WORK environment variable
        # work_path = os.getenv('WORK', '/mnt/share')
        #
        # image_path = os.path.join(work_path, f"{containerization_cfg.image_name}.sif")

        build_command = f"singularity build --fakeroot {cfg.containerization.singularity.image_name} docker://{cfg.paths.generated_files}"
        try:
            # Execute the Singularity build command
            subprocess.run(build_command, check=True, shell=True)
            print(
                f"Singularity image '{cfg.paths.generated_files}/{cfg.containerization.singularity.image_name}' built successfully."
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building Singularity image: {e}")
