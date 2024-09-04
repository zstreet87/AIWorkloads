#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to log messages with a timestamp
log() {
	echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# Load environment variables
log "Loading environment variables..."
source /etc/environment || true
source ~/.bashrc || true

# Check if the necessary environment variables are set
if [ -z "$CONFIG_PATH" ]; then
	log "ERROR: CONFIG_PATH environment variable is not set."
	exit 1
fi

# Detect GPU architecture and log CUDA or ROCm versions
if command -v nvidia-smi &>/dev/null; then
	# NVIDIA GPU detected
	log "NVIDIA GPU detected"
	log "CUDA version: $(nvcc --version || echo 'CUDA not installed')"
elif command -v rocminfo &>/dev/null; then
	# AMD GPU detected
	log "AMD GPU detected"
	log "ROCm version: $(rocminfo | grep -i 'ROCm Version' || echo 'ROCm not installed')"
else
	# No compatible GPU detected
	log "No compatible GPU (NVIDIA or AMD) detected."
fi

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
	log "Installing Python dependencies..."
	pip install --no-cache-dir -r requirements.txt
fi

# Architecture-specific setup
if command -v nvidia-smi &>/dev/null; then
	# NVIDIA-specific setup commands
	log "Running NVIDIA-specific setup..."
	# Example: export CUDA_VISIBLE_DEVICES to use only specific GPUs
	export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
elif command -v rocminfo &>/dev/null; then
	# AMD-specific setup commands
	log "Running AMD-specific setup..."
	# Example: Setup ROCm environment variables or configurations
	export ROCM_PATH=${ROCM_PATH:-/opt/rocm}
	export HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES:-0}
fi

# Run the main application script
log "Starting the main application..."
exec python src/aiworkloads/scripts/main.py --config-path "$CONFIG_PATH"
