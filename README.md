# Docker DDoS Testbed: Machine Learning & Deep Learning Model Deployment

## Reference to Complete MacOS, Linux, and Windows Results

For a detailed account of my research and findings, please refer to my Master's Thesis hosted on the Cal Poly Digital Commons which contains appendices for each:

[**My Thesis on Botnet Detection with Deep Learning**](https://digitalcommons.calpoly.edu/theses/2930/)

## Introduction

This project aims to provide a lightweight and simple testbed for Distributed Denial of Service (DDoS) detection using various machine learning and deep learning models. The testbed is based on Docker, which allows for the easy deployment and testing of pre-trained models. The testbed is designed to be simpler than network emulation tools like GNS3 or Mininet but effective enough to test model performance in detecting DDoS attacks.

### Models Included:
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- CNN-LSTM
- Hybrid Autoencoder with XGBoost

The testbed is a prototype environment to quickly deploy and test these models and evaluate their performance on detecting DDoS traffic. It is ideal for prototyping and research, providing a fast and simple alternative to more complex network setups.

## Prerequisites

**NOTE:** You need Anaconda for this environment; otherwise, it will not work.

- Anaconda: [Download and install Anaconda](https://www.anaconda.com/products/individual)
- Docker: [Download and install Docker](https://www.docker.com/)

## Setting up

### Setup the Environment

1. Clone the repository:
   ```sh
   git clone https://github.com/luisdavidgarcia/DDoS-Hybrid-Detection-System
   cd project-name
   ```

2. Run the setup script to create the environment and install dependencies:
   ```sh
   ./setup.sh
   ```

3. Activate your conda environment:
   ```sh
   conda activate docker-ddos-testbed
   ```

## Running the DDoS Testbed

Once the environment is set up, you can deploy and test machine learning models on the Docker-based testbed.

### Running the Docker Testbed

1. Ensure Docker is running on your system.
2. Deploy the testbed using Docker Compose:
   ```sh
   docker-compose up
   ```

3. The testbed will automatically set up the environment and run DDoS detection using the pre-configured machine learning models.

### Running the Models

Each model will be tested against the simulated network traffic within the Docker containers.

1. To run the pre-trained models (Logistic Regression, Decision Tree, Random Forest, XGBoost, CNN-LSTM, and Autoencoder-XGBoost), ensure the data is properly formatted and available for the models to process.
   
2. To train your own models or see how we trained them, please refer to the directory `notebooks/` and run the Jupyter notebooks to train the models, particulary the `results_nslk-kdd_binary.ipynb` notebook for binary classification.

This will load the dataset, preprocess it, and then evaluate the models' effectiveness in detecting DDoS attacks.

## Additional Information

### Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

### License

This project is licensed under the GNU License. See the LICENSE file for details.

### Troubleshooting

Common issues and solutions:

- **Docker Issues:** Ensure Docker is running correctly, and all containers are built without errors.
- **Model Prediction Errors:** Ensure that the dataset provided is correctly formatted and compatible with the pre-trained models.

### Contact

For questions or support, please open an issue in the repository or contact the project maintainer.
