#!/bin/bash

# Define environment name
ENV_NAME="ids_dl"

# Check if the operating system is macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "This script is intended only for macOS. Exiting."
  exit 1
fi

# Function to create conda environment
create_env() {
    echo "Creating a new conda environment named $ENV_NAME"
    conda create --name $ENV_NAME python=3.10 -y
    echo "Environment $ENV_NAME created."
}

# Function to install packages
install_packages() {
    echo "Activating $ENV_NAME and installing packages..."
    conda activate $ENV_NAME

    # Install TensorFlow; Conda should handle the architecture-specific build
    conda install -c anaconda tensorflow -y

    # Install additional required packages
    conda install -c anaconda pandas scikit-learn matplotlib -y
    conda install -c conda-forge spektral pyshark -y # Spektral for graph neural networks, pyshark for pcap file handling

    echo "All packages installed."
}

# Check for Conda and set up the environment
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found. Please install Miniconda or Anaconda first."
    exit
else
    echo "Conda is installed."
    create_env
    install_packages
fi

echo "Setup completed. Use 'conda activate $ENV_NAME' to activate the environment."

