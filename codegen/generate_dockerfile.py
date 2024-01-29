import os


def generate_dockerfile(dockerfile_cfg):
    dockerfile_content = f"FROM {dockerfile_cfg.base_image}\n"
    dockerfile_content += f"WORKDIR {dockerfile_cfg.workdir}\n"

    # Handling different distributions
    distro_cfg = dockerfile_cfg.packages.get(dockerfile_cfg.distro)
    dockerfile_content += f"RUN {distro_cfg.update_command}\n"

    # Install additional system packages based on distribution
    if distro_cfg.additional_packages:
        packages = " ".join(distro_cfg.additional_packages)
        dockerfile_content += f"RUN {distro_cfg.install_command} {packages}\n"

    # Copy required files
    for file in dockerfile_cfg.copy_files:
        dockerfile_content += f"COPY {file} {dockerfile_cfg.workdir}/\n"

    # Install Python packages
    dockerfile_content += "RUN pip install -r requirements.txt\n"

    if dockerfile_cfg.python_packages:
        python_packages = " ".join(dockerfile_cfg.python_packages)
        dockerfile_content += f"RUN pip install {python_packages}\n"

    # Build packages from source
    for package in dockerfile_cfg.build_from_source:
        if package.enabled:
            dockerfile_content += (
                f"RUN wget {package.url} -O /tmp/{package.name}.tar.gz \\\n"
            )
            dockerfile_content += (
                f"    && tar -xzf /tmp/{package.name}.tar.gz -C /tmp \\\n"
            )
            dockerfile_content += (
                f"    && cd /tmp/{package.name}-{package.version} \\\n"
            )
            for command in package.build_commands:
                dockerfile_content += f"    && {command} \\\n"
            dockerfile_content += "    && rm -rf /tmp/{}*\n".format(package.name)

    # Command to run
    dockerfile_content += f'CMD ["{dockerfile_cfg.command}"]\n'

    # Write the Dockerfile
    script_path = os.path.join(os.getcwd(), "Dockerfile")
    with open(script_path, "w") as file:
        file.write(dockerfile_content)
    print(f"Dockerfile script generated at {script_path}")
