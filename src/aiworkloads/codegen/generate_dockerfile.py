from pathlib import Path
from string import Template


def generate_dockerfile(cfg):
    base_template = Template(
        """FROM ${base_image}
WORKDIR ${workdir}
"""
    )

    run_command_template = Template("RUN ${command}\n")

    copy_command_template = Template("COPY ${source} ${destination}\n")

    entrypoint_template = Template(
        """COPY src/aiworkloads/scripts/docker_entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
"""
    )

    dockerfile_content = base_template.substitute(
        base_image=cfg.dockerfile.base_image, workdir=cfg.dockerfile.workdir
    )

    distro_cfg = cfg.dockerfile.packages.get(cfg.dockerfile.distro)
    dockerfile_content += run_command_template.substitute(
        command=distro_cfg.update_command
    )

    if distro_cfg.additional_packages:
        packages = " ".join(distro_cfg.additional_packages)
        install_command = f"{distro_cfg.install_command} {packages}"
        dockerfile_content += run_command_template.substitute(command=install_command)

    def generate_huggingface_commands(cfg):
        cmds = []
        cmds.append(
            copy_command_template.substitute(
                source=cfg.model_framework.huggingface.script,
                destination=cfg.dockerfile.workdir,
            )
        )
        cmds.append("RUN pip install -r requirements.txt\n")
        cmds.append(
            run_command_template.substitute(
                command="pip install "
                + " ".join(cfg.model_framework.huggingface.requirements)
            )
        )
        return "".join(cmds)

    model_framework_commands_map = {
        "huggingface": generate_huggingface_commands,
        # Add other model frameworks here as needed
    }

    if cfg.model_framework.type in model_framework_commands_map:
        dockerfile_content += model_framework_commands_map[cfg.model_framework.type](
            cfg
        )

    if cfg.dockerfile.python_packages:
        python_packages = " ".join(cfg.dockerfile.python_packages)
        dockerfile_content += run_command_template.substitute(
            command=f"pip install {python_packages}"
        )

    for package in cfg.dockerfile.build_from_source:
        if package.enabled:
            build_commands = (
                [
                    f"wget {package.url} -O /tmp/{package.name}.tar.gz \\",
                    f"tar -xzf /tmp/{package.name}.tar.gz -C /tmp \\",
                    f"cd /tmp/{package.name}-{package.version} \\",
                ]
                + [f"{command} \\" for command in package.build_commands]
                + [f"rm -rf /tmp/{package.name}*"]
            )
            for command in build_commands:
                dockerfile_content += run_command_template.substitute(command=command)

    dockerfile_content += entrypoint_template.substitute()

    script_path = Path(cfg.paths.cache) / "Dockerfile"
    script_path.write_text(dockerfile_content)
    print(f"Dockerfile script generated at {script_path}")
