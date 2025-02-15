import sys
import logging

sys.path.append('/models')
from base.utils import setup_logging
from base.base_model import BaseModel

if __name__ == "__main__":
    try:
        logger = setup_logging()
        
        model_dir = '/models/rf'
        logger.info(f"Setting up model with directory: {model_dir}")
        
        model = BaseModel(
            model_path=f'{model_dir}/random_forest_binary_model.joblib',
            scaler_path=f'{model_dir}/standard_scaler.joblib',
            flag_encoder_path=f'{model_dir}/flag_encoder.joblib',
            service_encoder_path=f'{model_dir}/service_encoder.joblib',
        )
        
        logger.info("Model initialized successfully")
        logger.info("Starting Suricata log streaming...")
        
        model.stream_suricata_logs()
    except Exception as e:
        logger.error(f"Main exception: {str(e)}", exc_info=True)
        raise