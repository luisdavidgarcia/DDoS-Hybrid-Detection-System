# General

## Conda Problems

I noticed over time if there are some issues with missing libraries just refer
to this stackoverflow post [problem after updating to conda23](https://stackoverflow.com/questions/77617946/solve-conda-libmamba-solver-libarchive-so-19-error-after-updating-conda-to-23)

## Getting Started with REACT

Just checkout the documenation: [REACT DOCS](https://react.dev/)

## Getting Started with DJANGO

Just checkout the documenation: [DJANGO DOCS](https://docs.djangoproject.com/en/5.0/)

## Conda Environments

This is why you can't use `conda init bash`

Here's what's happening:

1. `conda create --name $ENV_NAME python=$PYTHON_VERSION -y`: This command creates a new conda environment with the specified name and Python version. The -y flag is used to automatically answer "yes" to any prompts during the installation process.
2. `conda init bash`: This command is supposed to initialize the Bash shell for conda environments. However, it's not being executed correctly because the conda command is not available in the current shell session.
3. `conda activate $ENV_NAME`: This command attempts to activate the newly created conda environment, but it fails because the conda command is still not available in the current shell session.

To fix this issue, you need to either restart your terminal or run the source command to update the current shell session with the changes made by conda init bash. Here's how you can modify the script to ensure it works correctly:

1. Create the conda environment
    ```bash
    conda create --name $ENV_NAME python=$PYTHON_VERSION -y
    ```

2. Initialize the Bash shell for conda environments
    ```bash
    source "$(conda info --base)/etc/profile.d/conda.sh"
    ```

3. Activate the conda environment
    ```bash
    conda activate $ENV_NAME
    ```

## Checking Active Ports

For MacOS:

```bash
lsof -i -P -n | grep LISTEN
```

## Downloading Datasets

1. CICIDS 2017: [CICIDS 2017](https://www.unb.ca/cic/datasets/ids-2017.html)
    - Download link: [link](http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/)
2. CICIDS 2018: [CICIDS 2018](https://www.unb.ca/cic/datasets/ids-2018.html)
    - Download link: [link](http://205.174.165.80/CICDataset/CICDDoS2019/Dataset/)
3. CICIDS 2019: [CICIDS 2019](https://www.unb.ca/cic/datasets/ids-2019.html)
    - Download link: [link](http://205.174.165.80/CICDataset/CIC-IDS-2019/Dataset/)