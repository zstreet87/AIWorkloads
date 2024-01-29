import os
import subprocess

def build_and_save_image(dockerfile_path, image_name):
    # Get the path from the WORK environment variable
    work_path = os.getenv('WORK', '/mnt/share')

    # Construct the full path for the Singularity image
    image_path = os.path.join(work_path, f"{image_name}.sif")

    # Construct the Singularity build command
    build_command = f"singularity build --fakeroot {image_path} docker://{dockerfile_path}"

    try:
        # Execute the Singularity build command
        subprocess.run(build_command, check=True, shell=True)
        print(f"Singularity image '{image_path}' built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while building Singularity image: {e}")
