import json
import numpy as np
import tensorflow as tf
import logging
from collections import defaultdict
import joblib

# Configure logging
logging.basicConfig(filename='/var/log/suricata/cnn_lstm_predictions.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the CNN-LSTM model
cnn_lstm_model = tf.keras.models.load_model('/models/cnn_lstm_model_binary.keras')

# Initialize data structures to track `src_bytes` and `diff_srv_rate`
src_bytes_dict = defaultdict(int)
diff_srv_rate_dict = defaultdict(set)

# Batch storage for real-time prediction
batch_size = 64
batch_data = []

# Load encoders for service and flag features
service_encoder = joblib.load('/models/service_encoder.joblib')
flag_encoder = joblib.load('/models/flag_encoder.joblib')

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

# Function to preprocess the features for CNN-LSTM model
def preprocess_features(service, flag, src_bytes, diff_srv_rate):
    # Encode categorical features with pre-fitted encoders
    encoded_service = service_encoder.transform([service])[0] if service in service_encoder.classes_ else -1
    encoded_flag = flag_encoder.transform([flag])[0] if flag in flag_encoder.classes_ else -1

    # Create a feature array in the shape (1, 4, 1) for keras models
    features = np.array([[encoded_service, encoded_flag, src_bytes, diff_srv_rate]]).reshape(1, 4, 1)
    return features

# Function to process batches and make predictions
def process_batch():
    global batch_data

    # Convert batches to numpy arrays for prediction
    keras_batch = np.array(batch_data).reshape(-1, 4, 1)  # Shape for CNN-LSTM: (batch_size, 4, 1)

    # Predict using the CNN-LSTM model
    if len(keras_batch) > 0:
        keras_predictions = cnn_lstm_model.predict(keras_batch)
        # Log predictions to file
        logging.info(f"CNN-LSTM Batch Predictions: {keras_predictions}")

    # Clear the batch data after predictions
    batch_data.clear()

# Function to handle new log entries and accumulate batch data
def process_log_entry(log_entry):
    global batch_data

    # Extract relevant fields from the log entry
    src_ip = log_entry.get('src_ip')
    dest_port = log_entry.get('dest_port')
    proto = log_entry.get('proto')  # Protocol
    flow = log_entry.get('flow', {})
    tcp = log_entry.get('tcp', {})  # TCP flags
    bytes_toserver = flow.get('bytes_toserver', 0)

    # Treat protocol as the service
    service = proto

    # Extract src_bytes (bytes sent by the source IP)
    src_bytes = bytes_toserver

    # Extract TCP flags and map them to your dataset's flags
    flag = map_tcp_flags(tcp)  # Map Suricata TCP flags to your flag set
    
    # Track diff_srv_rate (distinct services accessed by the source IP)
    if src_ip and dest_port:
        diff_srv_rate_dict[src_ip].add(dest_port)
    
    # Store src_bytes for the current source IP
    src_bytes_dict[src_ip] += src_bytes
    
    # Get `diff_srv_rate` as the number of distinct services accessed by the src_ip
    diff_srv_rate = len(diff_srv_rate_dict[src_ip])

    # Preprocess features and accumulate batch data
    preprocessed_features = preprocess_features(service, flag, src_bytes, diff_srv_rate)
    batch_data.append(preprocessed_features)

    # Check if batch is full and process it
    if len(batch_data) >= batch_size:
        process_batch()

# Real-time log streaming
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
    with open(log_file_path, 'r') as log_file:
        log_file.seek(0, 2)  # Move to the end of the file
        while True:
            line = log_file.readline()  # Read new lines as they appear
            if line:
                try:
                    log_entry = json.loads(line)
                    process_log_entry(log_entry)
                except json.JSONDecodeError:
                    continue  # Skip invalid log lines
            else:
                continue  # Wait for new log entries

# Start real-time log streaming
if __name__ == "__main__":
    stream_suricata_logs()