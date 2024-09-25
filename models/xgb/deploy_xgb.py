# import json
# import logging
# import joblib
# import numpy as np
# from sklearn.preprocessing import StandardScaler

# filename = 'xgboost_binary_model'

# logging.basicConfig(
#     filename=f'/models/{filename}_predictions.log',
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# model = joblib.load(f'/models/{filename}.joblib')
# service_encoder = joblib.load('/models/service_encoder.joblib')
# flag_encoder = joblib.load('/models/flag_encoder.joblib')
# scaler = joblib.load('/models/standard_scaler.joblib') 

# batch_size = 64
# batch_data = []

# ############ Helper Functions ############
# def _map_service(dest_port):
#     service_port_mapping = {
#         194: 'IRC',            # Internet Relay Chat
#         6000: 'X11',           # X Window System
#         210: 'Z39_50',         # Z39.50 protocol
#         5190: 'aol',           # AOL Instant Messenger
#         113: 'auth',           # Authentication Service
#         179: 'bgp',            # Border Gateway Protocol
#         530: 'courier',        # RPC Courier service
#         105: 'csnet_ns',       # CSNET Name Service
#         84: 'ctf',             # Common Trace Facility
#         13: 'daytime',         # Daytime protocol
#         9: 'discard',          # Discard protocol
#         53: 'domain',          # DNS
#         53: 'domain_u',        # DNS (UDP)
#         7: 'echo',             # Echo protocol
#         7: 'eco_i',            # Echo protocol (ICMP)
#         7: 'ecr_i',            # Echo Reply (ICMP)
#         520: 'efs',            # Extended File System
#         512: 'exec',           # Remote Process Execution
#         79: 'finger',          # Finger protocol
#         21: 'ftp',             # FTP control
#         20: 'ftp_data',        # FTP data transfer
#         70: 'gopher',          # Gopher protocol
#         80: 'http',            # HTTP
#         2784: 'http_2784',     # HTTP (alternative port)
#         443: 'http_443',       # HTTPS
#         8001: 'http_8001',     # HTTP (alternative port)
#         143: 'imap4',          # IMAP (Internet Message Access Protocol)
#         102: 'iso_tsap',       # ISO Transport Service Access Point
#         543: 'klogin',         # Kerberos Login
#         544: 'kshell',         # Kerberos Remote Shell
#         389: 'ldap',           # Lightweight Directory Access Protocol
#         87: 'link',            # LINK protocol
#         513: 'login',          # Remote login
#         57: 'mtp',             # Message Transfer Protocol
#         42: 'name',            # Host Name Server
#         138: 'netbios_dgm',    # NetBIOS Datagram Service
#         137: 'netbios_ns',     # NetBIOS Name Service
#         139: 'netbios_ssn',    # NetBIOS Session Service
#         15: 'netstat',         # Network Statistics
#         433: 'nnsp',           # Network News Transfer Protocol over SSL
#         119: 'nntp',           # Network News Transfer Protocol
#         123: 'ntp_u',          # Network Time Protocol (UDP)
#         111: 'sunrpc',         # Sun Remote Procedure Call
#         514: 'shell',          # Remote Shell (RSH)
#         25: 'smtp',            # Simple Mail Transfer Protocol
#         1521: 'sql_net',       # Oracle SQL*Net
#         22: 'ssh',             # Secure Shell
#         111: 'sunrpc',         # Sun Remote Procedure Call
#         95: 'supdup',          # SUPDUP protocol
#         11: 'systat',          # System Status
#         23: 'telnet',          # Telnet protocol
#         69: 'tftp_u',          # Trivial File Transfer Protocol
#         37: 'time',            # Time protocol
#         4045: 'pm_dump',       # Process Monitoring
#         109: 'pop_2',          # Post Office Protocol version 2
#         110: 'pop_3',          # Post Office Protocol version 3
#         515: 'printer',        # Line Printer Daemon
#         9999: 'private',       # Private network (commonly user-assigned)
#         109: 'remote_job',     # Remote Job Entry
#         77: 'rje',             # Remote Job Entry
#         513: 'login',          # Remote Login (Kerberos)
#         67: 'urh_i',           # UDP Request Header (DHCP)
#         68: 'urp_i',           # UDP Response Header (DHCP)
#         540: 'uucp',           # Unix-to-Unix Copy Protocol
#         540: 'uucp_path',      # UUCP Path
#         175: 'vmnet',          # VMnet
#         43: 'whois'            # WHOIS protocol
#     }
#     return service_port_mapping.get(dest_port, 'other')

# def _map_tcp_flags(tcp_flags):
#     if not tcp_flags:
#         return 'OTH' 
#     if tcp_flags.get('syn') and tcp_flags.get('fin'):
#         return 'SF'
#     elif tcp_flags.get('syn') and not (tcp_flags.get('ack') or tcp_flags.get('fin')):
#         return 'S0'
#     elif tcp_flags.get('rst'):
#         return 'REJ'
#     elif tcp_flags.get('syn') and tcp_flags.get('rst'):
#         return 'RSTO'
#     elif tcp_flags.get('ack') and tcp_flags.get('rst'):
#         return 'RSTOS0'
#     elif tcp_flags.get('fin'):
#         return 'S1'
#     else:
#         return 'OTH'

# def _preprocess_features(service, flag, src_bytes, dst_bytes):
#     try:
#         encoded_service = service_encoder.transform([service])[0]
#     except ValueError:
#         return None

#     try:
#         encoded_flag = flag_encoder.transform([flag])[0]
#     except ValueError:
#         encoded_flag = flag_encoder.transform(['OTH'])[0]

#     features = np.array([encoded_service, encoded_flag, src_bytes, dst_bytes])
#     return features

# def _process_batch():
#     global batch_data

#     if len(batch_data) == 0:
#         return

#     features_list, metadata_list = zip(*batch_data)
#     joblib_batch = np.array(features_list)
#     joblib_batch_scaled = scaler.transform(joblib_batch)

#     joblib_probabilities = model.predict_proba(joblib_batch_scaled)[:, 1]
#     joblib_predictions = (joblib_probabilities >= 0.5).astype(int)

#     for prediction, probability, features, metadata in zip(joblib_predictions, joblib_probabilities, joblib_batch_scaled, metadata_list):
#         logging.info(
#             f"Prediction: {prediction}, Probability: {probability:.4f}, Features: {features.tolist()}, Metadata: {metadata}"
#         )

#     batch_data.clear()

# def _process_log_entry(log_entry):
#     global batch_data

#     event_type = log_entry.get('event_type')
#     if event_type == "stats":
#         return

#     src_ip = log_entry.get('src_ip')
#     if src_ip is None:
#         logging.error(f"Missing src_ip in log entry: {log_entry}")
#         return

#     dest_port = log_entry.get('dest_port')
#     proto = log_entry.get('proto')
#     flow = log_entry.get('flow', {})
#     tcp = log_entry.get('tcp', {})

#     src_bytes = flow.get('bytes_toserver', 0)
#     dst_bytes = flow.get('bytes_toclient', 0)

#     if src_bytes == 0 and dst_bytes == 0:
#         logging.warning(f"Missing bytes info. src_bytes: {src_bytes}, dst_bytes: {dst_bytes}")

#     service = _map_service(dest_port) if dest_port else 'other'
#     if proto == "ICMP":
#         service = "ecr_i"
#     flag = _map_tcp_flags(tcp)

#     preprocessed_features = _preprocess_features(service, flag, src_bytes, dst_bytes)
#     if preprocessed_features is not None:
#         metadata = {
#             'src_ip': src_ip,
#             'dest_port': dest_port,
#             'proto': proto,
#             'service': service,
#             'flag': flag,
#             'timestamp': log_entry.get('timestamp')
#         }
#         batch_data.append((preprocessed_features, metadata))
#     else:
#         return

#     if len(batch_data) >= batch_size:
#         _process_batch()

# ############ Main Function ############
# def stream_suricata_logs(log_file_path='/var/log/suricata/eve.json'):
#     with open(log_file_path, 'r') as log_file:
#         log_file.seek(0, 2)
#         while True:
#             line = log_file.readline()
#             if line:
#                 try:
#                     log_entry = json.loads(line)
#                     _process_log_entry(log_entry)
#                 except json.JSONDecodeError:
#                     logging.error(f"JSONDecodeError: {line.strip()}")
#                     continue
#             else:
#                 continue

# if __name__ == "__main__":
#     stream_suricata_logs()

import json
import logging
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from collections import defaultdict

filename = 'xgboost_binary_model'

logging.basicConfig(
    filename=f'/models/{filename}_predictions.log',
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