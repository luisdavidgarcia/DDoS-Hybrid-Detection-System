#!/bin/bash

# Variables
ENV_NAME="watchtower-env"
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
conda install -c conda-forge numpy pandas matplotlib -y

# Install Ollama client if available
pip install ollama

# # Create the Django project and app in the backend directory
# mkdir -p backend
# cd backend
# django-admin startproject $DJANGO_PROJECT_NAME
# cd $DJANGO_PROJECT_NAME
# python manage.py startapp $DJANGO_APP_NAME

# # Update Django settings to include the new app and Django REST framework
# SETTINGS_FILE="$DJANGO_PROJECT_NAME/settings.py"
# sed -i "" "s/INSTALLED_APPS = \[/INSTALLED_APPS = \[\n    '$DJANGO_APP_NAME',\n    'rest_framework',/" $SETTINGS_FILE

# # Create initial Django migration
# python manage.py makemigrations
# python manage.py migrate

# # Go back to the root directory
# cd ../../

# # Create the React project in the frontend directory
# mkdir -p frontend
# cd frontend
# npx create-react-app $REACT_APP_NAME
# cd $REACT_APP_NAME

# Output success message
echo "Conda environment '$ENV_NAME' has been set up with all dependencies."
echo "Django project '$DJANGO_PROJECT_NAME' with app '$DJANGO_APP_NAME' has been created."
echo "React project '$REACT_APP_NAME' has been created."
echo "Activate the environment using: conda activate $ENV_NAME"