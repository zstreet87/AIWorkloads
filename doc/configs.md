# Configuration Guide

## Overview

This guide explains the configuration setup for running model training workflows using Hydra.

## Configuration Files

1. **config.yaml**: Main configuration file that sets defaults and includes other configurations.
2. **containerization**: Contains YAML files for Docker and Singularity configurations.
3. **job_schedular**: Contains YAML files for SLURM and Kubernetes job scheduler configurations.
4. **model_framework**: Configurations for different model frameworks like Hugging Face, Superbench, etc.
5. **paths.yaml**: Defines paths for working directories, cache, and current working directory.
6. **workflow.yaml**: Specifies which workflow steps to execute.

## Adding a New Job Scheduler

To add a new job scheduler:

1. Create a new YAML file under `job_schedular/`.
2. Define the `type`, environment variables, and specific options.
3. Update `config.yaml` to include the new scheduler configuration if needed.

## Example Usage

To run with a custom configuration:

```bash
aiworkloads job_schedular=k8 containerization=singularity model_framework=superbench
```
