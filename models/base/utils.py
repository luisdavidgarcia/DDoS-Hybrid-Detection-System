import json
import logging
import os
from base.base_model import BaseModel

def setup_logging(
    base_dir='/models', 
    model_dir='rf', 
    log_filename='random_forest_predictions.log'
):
    """Set up logging configuration and create necessary directories"""
    log_dir = os.path.join(base_dir, model_dir)
    log_path = os.path.join(log_dir, log_filename)
    
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Writing to: {log_path}")
    
    return logger

def load_config(model_dir):
    """Load model configuration from JSON file."""
    config_path = os.path.join(model_dir, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)
