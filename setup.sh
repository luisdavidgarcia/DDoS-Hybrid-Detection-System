#!/bin/bash

# Name of the conda environment
ENV_NAME="ids_dl"

# Python version
PYTHON_VERSION="3.10"

# Create and activate the conda environment
conda create --name $ENV_NAME python=$PYTHON_VERSION -y
conda activate $ENV_NAME

# Install Django and Django REST framework
conda install -c conda-forge django djangorestframework -y

# Install TensorFlow
conda install -c conda-forge tensorflow -y

# Install scikit-learn and XGBoost
conda install -c conda-forge scikit-learn xgboost -y

# Install additional libraries
conda install -c conda-forge numpy pandas matplotlib -y

# Install Ollama client if available
pip install ollama

# Output success message
echo "Conda environment '$ENV_NAME' has been set up with all dependencies."
echo "Activate the environment using: conda activate $ENV_NAME"