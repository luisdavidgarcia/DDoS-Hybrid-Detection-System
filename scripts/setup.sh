#!/bin/bash

set -e

ENV_NAME="docker-ddos-testbed"
PYTHON_VERSION="3.11"

echo "Creating the conda environment: $ENV_NAME with Python $PYTHON_VERSION"
conda create --name "$ENV_NAME" python="$PYTHON_VERSION" -y

echo "Initializing conda..."
source "$(conda info --base)/etc/profile.d/conda.sh"

echo "Activating the environment: $ENV_NAME"
conda activate "$ENV_NAME"

echo "Installing TensorFlow..."
conda install tensorflow -y

echo "Installing scikit-learn and XGBoost..."
conda install scikit-learn xgboost -y

echo "Installing additional libraries (numpy, pandas, matplotlib, etc.)..."
conda install numpy pandas matplotlib imbalanced-learn psutil \
    seaborn jupyter -y

echo -e "\nCreating the directory for Nginx files..."
sh ./scripts/generate_files.sh

echo -e "\nConda environment '$ENV_NAME' has been set up with all dependencies."
echo "Activate the environment using: conda activate $ENV_NAME"