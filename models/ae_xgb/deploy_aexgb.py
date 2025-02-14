import json
import logging
import os
from ..base.base_model import BaseModel

filename = 'ae_xgb_binary_model'

logging.basicConfig(
    filename=f'{filename}_predictions.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

model = BaseModel(
    is_autoencoder=True,
    is_ml_model=False,
    model_path=f'{filename}.joblib',
    encoder_model_path='encoder_model.keras',
    scaler_path='standard_scaler.joblib',
    flag_encoder_path='flag_encoder.joblib',
    service_encoder_path='service_encoder.joblib',
    batch_size=64
)

############ Main Function ############
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
    with open(log_file_path, 'r') as log_file:
        log_file.seek(0, os.SEEK_END)
        while True:
            line = log_file.readline()
            if line:
                try:
                    log_entry = json.loads(line)
                    _process_log_entry(log_entry)
                except json.JSONDecodeError:
                    logging.error(f"JSONDecodeError: {line.strip()}")
                    continue
            else:
                continue

if __name__ == "__main__":
    stream_suricata_logs()
