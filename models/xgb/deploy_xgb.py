import json
import joblib
import numpy as np
import logging
from collections import defaultdict

# Setup logging configuration
logging.basicConfig(
    filename='/var/log/suricata/xgb_model_binary_predictions.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Load the XGBoost model
xgb_model = joblib.load('/models/xgboost_binary_model.joblib')

# Load the LabelEncoders for categorical features
service_encoder = joblib.load('/models/service_encoder.joblib')
flag_encoder = joblib.load('/models/flag_encoder.joblib')

# Initialize data structures
src_bytes_dict = defaultdict(int)
diff_srv_rate_dict = defaultdict(set)

# Batch storage for real-time prediction
batch_size = 64
batch_data = []

# Service mapping function
def map_service(dest_port):
    service_port_mapping = {
        20: 'ftp_data',
        21: 'ftp',
        22: 'ssh',
        23: 'telnet',
        25: 'smtp',
        53: 'domain',
        80: 'http',
        110: 'pop_3',
        111: 'sunrpc',
        113: 'auth',
        115: 'sftp',
        119: 'nntp',
        143: 'imap4',
        161: 'snmp',
        179: 'bgp',
        443: 'http_443',
        513: 'login',
        514: 'shell',
        587: 'smtp',
        993: 'imap4',
        995: 'pop_3',
        1080: 'socks',
        1524: 'ingreslock',
        2049: 'nfs',
        2121: 'ftp',
        3306: 'mysql',
        5432: 'postgresql',
        6667: 'IRC',
        8000: 'http',
        8080: 'http',
    }
    return service_port_mapping.get(dest_port, 'other')  # Default to 'other' if port is unknown

# Function to map Suricata TCP flags to your flag set
def map_tcp_flags(tcp_flags):
    if not tcp_flags:
        return 'OTH'  # Default to 'OTH' if flags are missing
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
        return 'OTH'  # Default to 'OTH' for unknown flags

# Function to preprocess the features
def preprocess_features(service, flag, src_bytes, diff_srv_rate):
    # Encode categorical features with pre-fitted encoders
    if service in service_encoder.classes_:
        encoded_service = service_encoder.transform([service])[0]
    else:
        return None  # Skip processing if service is unknown

    if flag in flag_encoder.classes_:
        encoded_flag = flag_encoder.transform([flag])[0]
    else:
        encoded_flag = flag_encoder.transform(['OTH'])[0]  # Set unknown flag to 'OTH'

    # Create a feature array
    features = np.array([encoded_service, encoded_flag, src_bytes, diff_srv_rate])
    return features

# Function to process batches and make predictions
def process_batch():
    global batch_data

    # Convert batches to numpy array for prediction
    joblib_batch = np.array(batch_data)  # Shape: (batch_size, 4)

    # Predict using the XGBoost model
    if len(joblib_batch) > 0:
        joblib_predictions = xgb_model.predict(joblib_batch)
        logging.info(f"XGBoost Batch Predictions: {joblib_predictions}")
        # Optionally, you can add more logic here to handle the predictions

    # Clear the batch data after predictions
    batch_data.clear()

# Function to handle new log entries and accumulate batch data
def process_log_entry(log_entry):
    global batch_data

    # Extract relevant fields from the log entry
    src_ip = log_entry.get('src_ip')
    dest_port = log_entry.get('dest_port')
    proto = log_entry.get('proto')  # Protocol field, e.g., 'TCP', 'UDP'
    flow = log_entry.get('flow', {})
    tcp = log_entry.get('tcp', {})  # TCP flags

    bytes_toserver = flow.get('bytes_toserver', 0)

    # Map the destination port to a service
    if dest_port:
        service = map_service(dest_port)
    else:
        service = 'other'

    # Extract src_bytes (bytes sent by the source IP)
    src_bytes = bytes_toserver

    # Map TCP flags
    flag = map_tcp_flags(tcp)

    # Track diff_srv_rate (distinct services accessed by the source IP)
    if src_ip and dest_port:
        diff_srv_rate_dict[src_ip].add(dest_port)
    
    # Get `diff_srv_rate` as the number of distinct services accessed by the src_ip
    diff_srv_rate = len(diff_srv_rate_dict[src_ip])

    # Preprocess features and accumulate batch data
    preprocessed_features = preprocess_features(service, flag, src_bytes, diff_srv_rate)
    if preprocessed_features is not None:
        batch_data.append(preprocessed_features)
    else:
        # Skip this entry due to unknown service
        logging.warning(f"Unknown service '{service}' encountered. Skipping entry.")
        return

    # Check if batch is full and process it
    if len(batch_data) >= batch_size:
        process_batch()

# Real-time log streaming
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
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

# Start real-time log streaming
if __name__ == "__main__":
    stream_suricata_logs()