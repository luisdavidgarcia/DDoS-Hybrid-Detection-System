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

# Install Django CORS headers
pip install django-cors-headers

# Install Ollama client
pip install ollama

# Navigate to the backend directory
cd backend/$DJANGO_PROJECT_NAME

# Update Django settings to include the new app and Django REST framework
SETTINGS_FILE="settings.py"
if ! grep -q "'$DJANGO_APP_NAME'" $SETTINGS_FILE; then
    sed -i "" "s/INSTALLED_APPS = \[/INSTALLED_APPS = \[\n    '$DJANGO_APP_NAME',\n    'corsheaders',\n    'rest_framework',/" $SETTINGS_FILE
    echo -e "\n# CORS settings\nCORS_ALLOW_ALL_ORIGINS = True\n" >> $SETTINGS_FILE
fi

# Create initial Django migration
python manage.py makemigrations
python manage.py migrate

# Navigate back to the root directory
cd ../../

# Navigate to the frontend directory
cd frontend/$REACT_APP_NAME

# Install React dependencies
npm install

# Output success message
echo "Conda environment '$ENV_NAME' has been set up with all dependencies."
echo "Django project '$DJANGO_PROJECT_NAME' with app '$DJANGO_APP_NAME' has been configured."
echo "React project '$REACT_APP_NAME' has been configured."
echo "Activate the environment using: conda activate $ENV_NAME"
