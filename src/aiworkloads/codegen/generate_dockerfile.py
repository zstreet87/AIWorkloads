import os


def generate_dockerfile(cfg):
    dockerfile_content = f"FROM {cfg.dockerfile.base_image}\n"
    dockerfile_content += f"WORKDIR {cfg.dockerfile.workdir}\n"

    distro_cfg = cfg.dockerfile.packages.get(cfg.dockerfile.distro)
    dockerfile_content += f"RUN {distro_cfg.update_command}\n"

    if distro_cfg.additional_packages:
        packages = " ".join(distro_cfg.additional_packages)
        dockerfile_content += f"RUN {distro_cfg.install_command} {packages}\n"

    if cfg.workload == "huggingface":
        dockerfile_content += (
            f"COPY {cfg.workload.huggingface.script} {cfg.dockerfile.workdir}/\n"
        )
        dockerfile_content += "RUN pip install -r requirements.txt\n"
        dockerfile_content += (
            "RUN pip install " + " ".join(cfg.workload.huggingface.requirements) + "\n"
        )

    if cfg.dockerfile.python_packages:
        python_packages = " ".join(cfg.dockerfile.python_packages)
        dockerfile_content += f"RUN pip install {python_packages}\n"

    for package in cfg.dockerfile.build_from_source:
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

    dockerfile_content += f'CMD ["{cfg.dockerfile.command}"]\n'

    script_path = os.path.join(cfg.paths.generated_files, "Dockerfile")
    with open(script_path, "w") as file:
        file.write(dockerfile_content)
    print(f"Dockerfile script generated at {script_path}")
