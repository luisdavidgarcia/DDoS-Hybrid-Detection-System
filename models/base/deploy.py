import sys
import os
import json
import logging
import argparse

sys.path.append('/models')
from base.utils import setup_logging, load_config
from base.base_model import BaseModel

def deploy_model(model_dir):
    """Deploy a model using its configuration file."""
    config = load_config(model_dir)
    
    logger = setup_logging(
        model_dir=config['model_type'],
        log_filename=f"{config['model_type']}_predictions.log"
    )
    logger.info(f"Setting up model with directory: {model_dir}")

    # Start with file paths which are always required
    model_params = {
        'model_path': os.path.join(model_dir, config['files']['model']),
        'scaler_path': os.path.join(model_dir, config['files']['scaler']),
        'flag_encoder_path': os.path.join(model_dir, config['files']['flag_encoder']),
        'service_encoder_path': os.path.join(model_dir, config['files']['service_encoder'])
    }

    if 'is_ml_model' in config:
        model_params['is_ml_model'] = config['is_ml_model']
    if 'is_hybrid' in config:
        model_params['is_hybrid'] = config['is_hybrid']

    if 'encoder' in config['files']:
        model_params['encoder_model_path'] = os.path.join(model_dir, config['files']['encoder'])

    for key, path in model_params.items():
        if 'path' in key and not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")

    model = BaseModel(**model_params)
    logger.info("Model initialized successfully")
    logger.info("Starting Suricata log streaming...")
    
    model.stream_suricata_logs()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy a model for network traffic analysis')
    parser.add_argument('--model-dir', type=str, default=None,
                       help='Directory containing the model files and config.json')
    args = parser.parse_args()

    try:
        # Use provided model_dir or fall back to script directory
        model_dir = args.model_dir or os.path.dirname(os.path.abspath(__file__))
        deploy_model(model_dir)
    except Exception as e:
        logging = logging.getLogger()
        logging.error(f"Main exception: {str(e)}", exc_info=True)
        raise