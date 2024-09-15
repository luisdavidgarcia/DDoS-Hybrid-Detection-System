import json
import numpy as np
import tensorflow as tf
import joblib
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(filename='/var/log/suricata/ae_xgb_predictions.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the AE-XGBoost model
ae_xgb_model = joblib.load('/models/xgboost_binary_model.joblib')

# Load the encoder model
encoder_model = tf.keras.models.load_model('/models/encoder_model.keras')

# Load the LabelEncoders for categorical features
service_encoder = joblib.load('/models/service_encoder.joblib')
flag_encoder = joblib.load('/models/flag_encoder.joblib')

# Initialize data structures to track `src_bytes` and `diff_srv_rate`
src_bytes_dict = defaultdict(int)
diff_srv_rate_dict = defaultdict(set)

# Batch storage for real-time prediction
batch_size = 64
batch_data = []

# Function to map Suricata TCP flags to your flag set
def map_tcp_flags(tcp_flags):
    if tcp_flags.get('syn') and tcp_flags.get('fin'):
        return 'SF'
    elif tcp_flags.get('syn') and not (tcp_flags.get('ack') or tcp_flags.get('fin')):
        return 'S0'
    elif tcp_flags.get('rst'):
        return 'REJ'
    elif tcp_flags.get('syn') and tcp_flags.get('rst'):
        return 'RSTO'
    elif tcp_flags.get('ack') and tcp_flags.get('rst'):
        return 'RSTOS0'
    elif tcp_flags.get('fin'):
        return 'S1'
    else:
        return 'OTH'

# Function to preprocess and encode the features
def preprocess_and_encode_features(service, flag, src_bytes, diff_srv_rate):
    try:
        # Encode categorical features with pre-fitted encoders
        encoded_service = service_encoder.transform([service])[0] if service in service_encoder.classes_ else -1
        encoded_flag = flag_encoder.transform([flag])[0] if flag in flag_encoder.classes_ else -1

        # Create a feature array
        features = np.array([[encoded_service, encoded_flag, src_bytes, diff_srv_rate]])

        # Reshape and encode the features using the trained encoder model
        features_reshaped = features.reshape((features.shape[0], features.shape[1], 1))
        encoded_features = encoder_model.predict(features_reshaped)

        # Flatten the encoded data for XGBoost
        encoded_features_flat = encoded_features.reshape((encoded_features.shape[0], -1))
        return encoded_features_flat

    except Exception as e:
        logging.error(f"Error during preprocessing or encoding: {str(e)}")
        return None

# Function to process batches and make predictions
def process_batch():
    global batch_data

    try:
        # Process and encode the batch data
        encoded_batch = np.vstack([preprocess_and_encode_features(*data) for data in batch_data if preprocess_and_encode_features(*data) is not None])

        if len(encoded_batch) > 0:
            # Predict using the AE-XGBoost model
            predictions = ae_xgb_model.predict(encoded_batch)
            logging.info(f"AE-XGBoost Batch Predictions: {predictions}")
        else:
            logging.error("Empty batch or error in preprocessing. Skipping predictions.")

    except Exception as e:
        logging.error(f"Error during batch processing: {str(e)}")

    finally:
        # Clear the batch data after predictions
        batch_data.clear()

# Function to handle new log entries and accumulate batch data
def process_log_entry(log_entry):
    global batch_data

    try:
        # Extract relevant fields from the log entry
        src_ip = log_entry.get('src_ip')
        dest_port = log_entry.get('dest_port')
        proto = log_entry.get('proto')
        flow = log_entry.get('flow', {})
        tcp = log_entry.get('tcp', {})
        bytes_toserver = flow.get('bytes_toserver', 0)

        # Extract and map features
        service = proto
        src_bytes = bytes_toserver
        flag = map_tcp_flags(tcp)

        # Track and store network statistics
        if src_ip and dest_port:
            diff_srv_rate_dict[src_ip].add(dest_port)
        src_bytes_dict[src_ip] += src_bytes
        diff_srv_rate = len(diff_srv_rate_dict[src_ip])

        # Accumulate preprocessed and encoded batch data
        batch_data.append((service, flag, src_bytes, diff_srv_rate))

        # Check if batch is full and process it
        if len(batch_data) >= batch_size:
            process_batch()

    except Exception as e:
        logging.error(f"Error processing log entry: {str(e)}")

# Real-time log streaming
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
    try:
        with open(log_file_path, 'r') as log_file:
            log_file.seek(0, 2)  # Move to the end of the file
            while True:
                line = log_file.readline()
                if line:
                    try:
                        log_entry = json.loads(line)
                        process_log_entry(log_entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid log lines
                else:
                    continue  # Wait for new log entries
    except Exception as e:
        logging.error(f"Error reading log file: {str(e)}")

# Start real-time log streaming
if __name__ == "__main__":
    stream_suricata_logs()