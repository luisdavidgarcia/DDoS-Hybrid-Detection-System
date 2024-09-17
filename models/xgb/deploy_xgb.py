import json
import joblib
import numpy as np
import logging
from collections import defaultdict

from sklearn.preprocessing import StandardScaler

# Setup logging configuration
logging.basicConfig(
    filename='/var/log/suricata/xgb_model_binary_predictions.log',
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the XGBoost model and pre-fitted scaler
xgb_model = joblib.load('/models/xgboost_binary_model.joblib')
scaler = joblib.load('/models/standard_scaler.joblib')

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
        # Port-to-service mappings
        20: 'ftp_data', 21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
        53: 'domain', 80: 'http', 110: 'pop_3', 111: 'sunrpc', 113: 'auth',
        115: 'sftp', 119: 'nntp', 143: 'imap4', 161: 'snmp', 179: 'bgp',
        443: 'http_443', 513: 'login', 514: 'shell', 587: 'smtp', 993: 'imap4',
        995: 'pop_3', 1080: 'socks', 1524: 'ingreslock', 2049: 'nfs',
        2121: 'ftp', 3306: 'mysql', 5432: 'postgresql', 6667: 'IRC',
        8000: 'http', 8080: 'http',
    }
    return service_port_mapping.get(dest_port, 'other')

# Function to map Suricata TCP flags to your flag set
def map_tcp_flags(tcp_flags):
    if not tcp_flags:
        return 'OTH'  # Default if flags are missing
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

# Function to preprocess the features
def preprocess_features(service, flag, src_bytes, diff_srv_rate):
    # Encode categorical features
    try:
        encoded_service = service_encoder.transform([service])[0]
    except ValueError:
        logging.warning(f"Unknown service '{service}'. Skipping entry.")
        return None  # Skip if service is unknown

    try:
        encoded_flag = flag_encoder.transform([flag])[0]
    except ValueError:
        logging.debug(f"Unknown flag '{flag}'. Setting to 'OTH'.")
        encoded_flag = flag_encoder.transform(['OTH'])[0]

    features = np.array([encoded_service, encoded_flag, src_bytes, diff_srv_rate])
    logging.debug(f"Encoded features: {features}")
    return features

# Function to process batches and make predictions
def process_batch():
    global batch_data

    if len(batch_data) == 0:
        return

    # Separate features and metadata
    features_list, metadata_list = zip(*batch_data)
    joblib_batch = np.array(features_list)

    logging.debug(f"Batch before scaling: {joblib_batch}")

    # Scale features using the pre-fitted scaler
    joblib_batch_scaled = scaler.transform(joblib_batch)

    logging.debug(f"Batch after scaling: {joblib_batch_scaled}")

    # Predict probabilities and class labels
    joblib_probabilities = xgb_model.predict_proba(joblib_batch_scaled)[:, 1]
    joblib_predictions = (joblib_probabilities >= 0.5).astype(int)

    # Log detailed predictions
    for prediction, probability, features, metadata in zip(joblib_predictions, joblib_probabilities, joblib_batch_scaled, metadata_list):
        logging.info(
            f"Prediction: {prediction}, Probability: {probability:.4f}, Features: {features.tolist()}, Metadata: {metadata}"
        )

    # Clear batch data
    batch_data.clear()

# Function to handle new log entries
def process_log_entry(log_entry):
    global batch_data

    # Extract relevant fields
    src_ip = log_entry.get('src_ip')
    dest_port = log_entry.get('dest_port')
    proto = log_entry.get('proto')
    flow = log_entry.get('flow', {})
    tcp = log_entry.get('tcp', {})

    bytes_toserver = flow.get('bytes_toserver', 0)

    # Map service and flags
    service = map_service(dest_port) if dest_port else 'other'
    flag = map_tcp_flags(tcp)

    # Calculate src_bytes and diff_srv_rate
    src_bytes = bytes_toserver
    if src_ip and dest_port:
        diff_srv_rate_dict[src_ip].add(dest_port)
    diff_srv_rate = len(diff_srv_rate_dict[src_ip])

    # Log raw inputs
    logging.debug(
        f"Raw input - src_ip: {src_ip}, dest_port: {dest_port}, proto: {proto}, "
        f"service: {service}, flag: {flag}, src_bytes: {src_bytes}, diff_srv_rate: {diff_srv_rate}"
    )

    # Preprocess features
    preprocessed_features = preprocess_features(service, flag, src_bytes, diff_srv_rate)
    if preprocessed_features is not None:
        metadata = {
            'src_ip': src_ip,
            'dest_port': dest_port,
            'proto': proto,
            'service': service,
            'flag': flag,
            'timestamp': log_entry.get('timestamp')
        }
        batch_data.append((preprocessed_features, metadata))
    else:
        # Entry skipped due to unknown service
        return

    # Process batch if full
    if len(batch_data) >= batch_size:
        process_batch()

# Real-time log streaming
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
    with open(log_file_path, 'r') as log_file:
        log_file.seek(0, 2)  # Move to end of file
        while True:
            line = log_file.readline()
            if line:
                try:
                    log_entry = json.loads(line)
                    process_log_entry(log_entry)
                except json.JSONDecodeError:
                    logging.error(f"JSONDecodeError: {line.strip()}")
                    continue
            else:
                continue

if __name__ == "__main__":
    stream_suricata_logs()