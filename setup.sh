#!/bin/bash

# Exit the script immediately if any command fails
set -e

# Variables
ENV_NAME="docker-ddos-testbed"
PYTHON_VERSION="3.10"

# Create the conda environment
echo "Creating the conda environment: $ENV_NAME with Python $PYTHON_VERSION"
conda create --name "$ENV_NAME" python="$PYTHON_VERSION" -y

# Initialize the Bash shell for conda environments
echo "Initializing conda..."
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate the conda environment
echo "Activating the environment: $ENV_NAME"
conda activate "$ENV_NAME"

# Install TensorFlow
echo "Installing TensorFlow..."
conda install -c conda-forge tensorflow -y

# Install scikit-learn and XGBoost
echo "Installing scikit-learn and XGBoost..."
conda install -c conda-forge scikit-learn xgboost -y

# Install additional libraries
echo "Installing additional libraries (numpy, pandas, matplotlib, etc.)..."
conda install -c conda-forge numpy pandas matplotlib imbalanced-learn psutil seaborn jupyter -y

# Output success message
echo "Conda environment '$ENV_NAME' has been set up with all dependencies."
echo "Activate the environment using: conda activate $ENV_NAME"