import json
import logging
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from collections import defaultdict

filename = ''

logging.basicConfig(
    filename=f'/var/log/suricata/{filename}_predictions.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

model = joblib.load(f'/models/{filename}.joblib')
service_encoder = joblib.load('/models/service_encoder.joblib')
flag_encoder = joblib.load('/models/flag_encoder.joblib')
scaler = joblib.load('/models/standard_scaler.joblib') 

src_bytes_dict = defaultdict(int)
diff_srv_rate_dict = defaultdict(set)
batch_size = 64
batch_data = []

############ Helper Functions ############
def _map_service(dest_port):
    service_port_mapping = {
        20: 'ftp_data', 21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
        53: 'domain', 80: 'http', 110: 'pop_3', 111: 'sunrpc', 113: 'auth',
        115: 'sftp', 119: 'nntp', 143: 'imap4', 161: 'snmp', 179: 'bgp',
        443: 'http_443', 513: 'login', 514: 'shell', 587: 'smtp', 993: 'imap4',
        995: 'pop_3', 1080: 'socks', 1524: 'ingreslock', 2049: 'nfs',
        2121: 'ftp', 3306: 'mysql', 5432: 'postgresql', 6667: 'IRC',
        8000: 'http', 8080: 'http'
    }
    return service_port_mapping.get(dest_port, 'other')

def _map_tcp_flags(tcp_flags):
    if not tcp_flags:
        return 'OTH' 
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

def _preprocess_features(service, flag, src_bytes, diff_srv_rate):
    try:
        encoded_service = service_encoder.transform([service])[0]
    except ValueError:
        logging.warning(f"Unknown service '{service}'. Skipping entry.")
        return None

    try:
        encoded_flag = flag_encoder.transform([flag])[0]
    except ValueError:
        logging.debug(f"Unknown flag '{flag}'. Setting to 'OTH'.")
        encoded_flag = flag_encoder.transform(['OTH'])[0]

    features = np.array([encoded_service, encoded_flag, src_bytes, diff_srv_rate])
    logging.debug(f"Encoded features: {features}")
    return features

def _process_batch():
    global batch_data

    if len(batch_data) == 0:
        return

    features_list, metadata_list = zip(*batch_data)
    joblib_batch = np.array(features_list)

    logging.debug(f"Batch before scaling: {joblib_batch}")

    joblib_batch_scaled = scaler.transform(joblib_batch)

    logging.debug(f"Batch after scaling: {joblib_batch_scaled}")

    joblib_probabilities = model.predict_proba(joblib_batch_scaled)[:, 1]
    joblib_predictions = (joblib_probabilities >= 0.5).astype(int)

    for prediction, probability, features, metadata in zip(joblib_predictions, joblib_probabilities, joblib_batch_scaled, metadata_list):
        logging.info(
            f"Prediction: {prediction}, Probability: {probability:.4f}, Features: {features.tolist()}, Metadata: {metadata}"
        )

    batch_data.clear()

def _process_log_entry(log_entry):
    global batch_data

    event_type = log_entry.get('event_type')
    if event_type == "stats":
        logging.debug("Skipping stats log entry.")
        return

    src_ip = log_entry.get('src_ip')
    if src_ip is None:
        logging.debug("Skipping log entry due to missing src_ip.")
        return

    dest_port = log_entry.get('dest_port')
    proto = log_entry.get('proto')
    flow = log_entry.get('flow', {})
    tcp = log_entry.get('tcp', {})

    bytes_toserver = flow.get('bytes_toserver', 0)

    service = _map_service(dest_port) if dest_port else 'other'
    if proto == "ICMP":
        service = "ecr_i"
    flag = _map_tcp_flags(tcp)

    src_bytes = bytes_toserver
    if src_ip and dest_port:
        diff_srv_rate_dict[src_ip].add(dest_port)
    diff_srv_rate = len(diff_srv_rate_dict[src_ip])

    logging.debug(
        f"Raw input - src_ip: {src_ip}, dest_port: {dest_port}, proto: {proto}, "
        f"service: {service}, flag: {flag}, src_bytes: {src_bytes}, diff_srv_rate: {diff_srv_rate}"
    )

    preprocessed_features = _preprocess_features(service, flag, src_bytes, diff_srv_rate)
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
        return

    if len(batch_data) >= batch_size:
        _process_batch()

############ Main Function ############
def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
    with open(log_file_path, 'r') as log_file:
        log_file.seek(0, 2)
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