# Real-Time DDoS Detection Using a Docker-Based Machine Learning Testbed

**Status Update:** Currently under review for publication at ISICN 2025

If you use this work in your research, please cite:

```bibtex
@mastersthesis{garcia2024dockerddos,
    title = {Real-Time Network Simulations for {ML}/{DL} {DDoS} Detection Using {Docker}},
    author = {Garcia, Luis D.},
    year = 2024,
    month = {December},
    address = {San Luis Obispo, CA},
    note = {Available at \url{https://digitalcommons.calpoly.edu/theses/2930/}},
    school = {California Polytechnic State University, San Luis Obispo}
}
```

## Introduction

This research presents a lightweight testbed for Distributed Denial of Service 
(DDoS) detection leveraging machine learning and deep learning models. Built on 
Docker containerization, the system offers a streamlined alternative to complex 
network emulation tools like GNS3 or Mininet while maintaining robust detection 
capabilities.

The testbed facilitates:
- Rapid deployment of pre-trained models
- Real-time network traffic analysis
- Efficient DDoS attack detection
- Simplified testing and validation procedures

## Reference Implementation

For comprehensive experimental results across macOS, Linux, and Windows 
environments, please refer to the complete Master's Thesis available through 
Cal Poly Digital Commons:

[Real-Time DDoS Detection Using a Docker-Based Machine Learning Testbed](https://digitalcommons.calpoly.edu/theses/2930/)

The thesis includes detailed appendices documenting platform-specific 
implementations and findings.

### Models Included:
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- CNN-LSTM
- Hybrid Autoencoder with XGBoost

The testbed is a prototype environment to quickly deploy and test these models 
and evaluate their performance on detecting DDoS traffic. It is ideal for 
prototyping and research, providing a fast and simple alternative to more 
complex network setups.

## Prerequisites

**NOTE:** Anaconda is highly recommended for this environment, especially for 
running the notebooks and training models. While alternative Python virtual 
environments (like `venv`) *might* work, they have not been thoroughly tested. 
Anaconda ensures consistent dependency management and is strongly suggested for 
a smooth experience.

- Anaconda: [Download and install Anaconda](https://www.anaconda.com/products/individual)

- Docker: [Download and install Docker](https://www.docker.com/)

**Important:** Anaconda is primarily required for the interactive notebooks and 
model training processes. It is not necessary for running the testbed environment.

## Setting up

### Setup the Environment

1. Clone the repository:
   ```sh
   git clone https://github.com/luisdavidgarcia/DDoS-Hybrid-Detection-System
   cd DDoS-Hybrid-Detection-System
   ```

2. Run the `setup,sh` script to create the environment and install dependencies:
   ```sh
   ./scripts/setup.sh
   ```

3. Activate your conda environment:
   ```sh
   conda activate docker-ddos-testbed
   ```

### Model Training and Evaluation

### Model Training and Evaluation

1. For pre-trained model evaluation (all supported models), ensure your data 
follows the required format.

2. Available training notebooks in the `notebooks/` directory:

   - **`results_nslk-kdd_binary.ipynb`**: **Binary NSL-KDD Notebook (Use this 
   one for training and evaluation).** This notebook contains a comprehensive 
   binary classification comparative analysis. All analysis scripts within the 
   `analysis/` directory are designed to align with the binary classification 
   results produced by this notebook.

   - `results_cicids2018.ipynb`: Analysis of CICIDS2018 dataset metrics. This 
   notebook is primarily intended for investigative purposes.

   - `results_nslk-kdd_multiclass.ipynb`: Experimental multiclass DDoS detection. 
   This notebook is primarily intended for investigative purposes.

   Each notebook includes:
   - Data preprocessing steps
   - Model training procedures
   - Evaluation metrics and analysis
   - Detailed documentation of findings

### Important Note on Datasets

While this project includes analyses using NSL-KDD and CICIDS2018 datasets for 
comparative purposes with existing literature, we strongly recommend:

- **Generate Your Own Dataset**: Use the testbed to create datasets that match 
   your specific network conditions and attack patterns
- **Real-World Training**: Train models on traffic data from your actual network 
   environment
- **Custom Validation**: Develop validation procedures specific to your 
   deployment scenario

The included datasets (NSL-KDD and CICIDS2018) should be viewed as reference 
implementations rather than production-ready solutions. For real-world 
applications, custom dataset generation using the testbed is strongly recommended.

### Models Directory

The `models/` directory contains model-specific subdirectories that are shared 
with Docker containers. Each model (ae_xgb, cnn_lstm, dt, lr, rf, xgb) has its 
own directory where you should place:

- Model files specific to that algorithm
- Required encoders and preprocessors
- `config.json` - defines model inputs and parameters

The `models/base/` directory contains:
- Base model class implementations
- Deployment scripts
- Shared utility functions

**Important:** When adding your own models or preprocessors, place them in their 
respective model directories to ensure proper Docker container access.

## Running the DDoS Testbed

Once the environment is set up, you can deploy and test machine learning models 
on the Docker-based testbed.

### Running the Docker Testbed

1. Ensure Docker is running on your system.
2. Deploy the testbed using the `startup.sh` script:
   ```sh
   ./scripts/startup.sh
   ```

3. The testbed will automatically set up the environment and run DDoS detection 
using the pre-configured machine learning models.

### Analyzing Results

1. After the simulation complete, you can view the Suricata logs in generated 
   `logs/` directory.

2. Model predicitions and features will be saved in logs respective to the 
   model directory in `models/` directory.

4. The `analysis/` directory contains scripts for analyzing the logs and 
   generating reports.

5. Start with the one you need and you only need to input the file paths
   for the logs you want to analyze.

## Additional Information

### License

This project is licensed under the GNU License. See the [LICENSE](./LICENSE) 
file for details.

### Troubleshooting

Common issues and solutions:

- **Docker Issues:** Ensure Docker is running correctly, and all containers are 
built without errors.
- **Model Prediction Errors:** Ensure that the dataset provided is correctly 
formatted and compatible with the pre-trained models.

### Leveraging Apache Benchmark 

A new docker compose file: `docker-compose.arm.ab.yml` is included, 
which significantly leads to the `nginx_web` container having CPU
usage of 100\% or more. 

This is due to the fact that the `ab`(apache benchmark) tool is used 
to generate a large amount of traffic to the `nginx_web` container. 
This is a great way to test the performance of the DDoS detection 
system in a controlled environment.
