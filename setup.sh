#!/bin/bash

# Variables
ENV_NAME="watchtower_env"
PYTHON_VERSION="3.10"
DJANGO_PROJECT_NAME="watchtower"
DJANGO_APP_NAME="alertsystem"
REACT_APP_NAME="watchtower-frontend"

# Create the conda environment
conda create --name $ENV_NAME python=$PYTHON_VERSION -y
# Initialize the Bash shell for conda environments
source "$(conda info --base)/etc/profile.d/conda.sh"
# Activate the conda environment
conda activate $ENV_NAME

# Reinstall sqlite to fix potential SQLite3 issues
conda install -c conda-forge sqlite -y

# Install Django and Django REST framework
conda install -c conda-forge django djangorestframework -y

# Install TensorFlow
conda install -c conda-forge tensorflow -y

# Install scikit-learn and XGBoost
conda install -c conda-forge scikit-learn xgboost -y

# Install additional libraries
conda install -c conda-forge numpy pandas matplotlib imbalanced-learn -y

# Install Django CORS headers
pip install django-cors-headers

# Install Ollama client
pip install ollama

# Navigate to the frontend directory
cd frontend/$REACT_APP_NAME

# Install React dependencies
npm install

# Go back to the root directory
cd ../..

# Output success message
echo "Conda environment '$ENV_NAME' has been set up with all dependencies."
echo "Django project '$DJANGO_PROJECT_NAME' with app '$DJANGO_APP_NAME' has been configured."
echo "React project '$REACT_APP_NAME' has been configured."
echo "Activate the environment using: conda activate $ENV_NAME"
