import json
import logging
import joblib
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
from enum import Enum
from typing import Dict, Optional

class TCPState(Enum):
    S0 = "S0"   # Connection attempt seen, no reply
    S1 = "S1"   # SYN without ACK, not usual behavior
    SF = "SF"   # Normal establishment and termination
    REJ = "REJ" # Connection attempt rejected
    OTH = "OTH" # Other

class BaseModel:

    _PORT_TO_SERVICE = {
        7: 'echo',             # Echo protocol
        9: 'discard',          # Discard protocol
        11: 'systat',          # System Status
        13: 'daytime',         # Daytime protocol
        15: 'netstat',         # Network Statistics
        20: 'ftp_data',        # FTP data transfer
        21: 'ftp',             # FTP control
        22: 'ssh',             # Secure Shell
        23: 'telnet',          # Telnet protocol
        25: 'smtp',            # Simple Mail Transfer Protocol
        37: 'time',            # Time protocol
        42: 'name',            # Host Name Server
        43: 'whois',           # WHOIS protocol
        53: 'domain',          # DNS
        57: 'mtp',             # Message Transfer Protocol
        67: 'urh_i',           # UDP Request Header (DHCP)
        68: 'urp_i',           # UDP Response Header (DHCP)
        69: 'tftp_u',          # Trivial File Transfer Protocol
        70: 'gopher',          # Gopher protocol
        77: 'rje',             # Remote Job Entry
        79: 'finger',          # Finger protocol
        80: 'http',            # HTTP
        84: 'ctf',             # Common Trace Facility
        87: 'link',            # LINK protocol
        95: 'supdup',          # SUPDUP protocol
        102: 'iso_tsap',       # ISO Transport Service Access Point
        105: 'csnet_ns',       # CSNET Name Service
        109: 'pop_2',          # Post Office Protocol version 2
        110: 'pop_3',          # Post Office Protocol version 3
        111: 'sunrpc',         # Sun Remote Procedure Call
        113: 'auth',           # Authentication Service
        119: 'nntp',           # Network News Transfer Protocol
        123: 'ntp_u',          # Network Time Protocol (UDP)
        137: 'netbios_ns',     # NetBIOS Name Service
        138: 'netbios_dgm',    # NetBIOS Datagram Service
        139: 'netbios_ssn',    # NetBIOS Session Service
        143: 'imap4',          # IMAP (Internet Message Access Protocol)
        175: 'vmnet',          # VMnet
        179: 'bgp',            # Border Gateway Protocol
        194: 'IRC',            # Internet Relay Chat
        210: 'Z39_50',         # Z39.50 protocol
        389: 'ldap',           # Lightweight Directory Access Protocol
        433: 'nnsp',           # Network News Transfer Protocol over SSL
        443: 'http_443',       # HTTPS
        512: 'exec',           # Remote Process Execution
        513: 'login',          # Remote Login (Kerberos)
        514: 'shell',          # Remote Shell (RSH)
        515: 'printer',        # Line Printer Daemon
        520: 'efs',            # Extended File Service
        530: 'courier',        # RPC Courier service
        540: 'uucp',           # Unix-to-Unix Copy Protocol
        543: 'klogin',         # Kerberos Login
        544: 'kshell',         # Kerberos Remote Shell
        1521: 'sql_net',       # Oracle SQL*Net
        2784: 'http_2784',     # HTTP (alternative port)
        4045: 'pm_dump',       # Process Monitoring
        5190: 'aol',           # AOL Instant Messenger
        6000: 'X11',           # X Window System
        8001: 'http_8001',     # HTTP (alternative port)
        9999: 'private'        # Private network (commonly user-assigned)
    }

    def __init__(
        self, 
        is_ml_model: bool = True,
        is_autoencoder: bool = False,
        model_path: str = None,
        encoder_model_path: str = None,
        scaler_path: str = None,
        flag_encoder_path: str = None,
        service_encoder_path: str = None,
        batch_size: int = 64,
        probability_ratio: float = 0.5
    ):
        self.encoder = None
        self.probability_ratio = probability_ratio

        if is_autoencoder:
            self.encoder = tf.keras.models.load_model(encoder_model_path)

        if not is_ml_model and not is_autoencoder:
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = joblib.load(model_path)
        
        self.scaler = joblib.load(scaler_path)
        self.flag_encoder = joblib.load(flag_encoder_path)
        self.service_encoder = joblib.load(service_encoder_path)
        self.batch_size = batch_size
        self.batch_data = []
    
    def process_log_entry(self, log_entry):
        event_type = log_entry.get('event_type')
        if event_type != "flow":
            return

        src_ip = log_entry.get('src_ip')
        dest_port = log_entry.get('dest_port')
        proto = log_entry.get('proto')
        flow = log_entry.get('flow', {})
        tcp = log_entry.get('tcp', {})

        src_bytes = flow.get('bytes_toserver', 0)
        dst_bytes = flow.get('bytes_toclient', 0)
        flow_state = flow.get('state', "")
        flow_reason = flow.get('reason', "")

        service = self._PORT_TO_SERVICE.get(dest_port, 'other')
        flag = self._map_tcp_flags(tcp, flow_state, flow_reason)

        preprocessed_features = self._preprocess_features(
            service, 
            flag, 
            src_bytes, 
            dst_bytes
        )
        if preprocessed_features is not None:
            metadata = {
                'src_ip': src_ip,
                'dest_port': dest_port,
                'proto': proto,
                'service': service,
                'flag': flag,
                'src_bytes': src_bytes,
                'dst_bytes': dst_bytes,
                'timestamp': log_entry.get('timestamp')
            }
            self.batch_data.append((preprocessed_features, metadata))

        if len(self.batch_data) >= self.batch_size:
            self._process_batch()

    def _map_tcp_flags(self, tcp_flags, flow_state, flow_reason):
        if not tcp_flags:
            if flow_state == "new" and flow_reason == "timeout":
                return TCPState.S0
            return TCPState.OTH

        if tcp_flags.get('syn') and not tcp_flags.get('ack'):
            if flow_state == "new" and flow_reason == "timeout":
                return TCPState.S0
            return TCPState.S1
        
        if tcp_flags.get('syn') and tcp_flags.get('ack'):
            return TCPState.SF
        
        if tcp_flags.get('rst'):
            return TCPState.REJ
        
        return TCPState.OTH

    def _preprocess_features(self, service, flag, src_bytes, dst_bytes):
        try:
            encoded_service = self.service_encoder.transform([service])[0]
        except ValueError:
            return None

        try:
            encoded_flag = self.flag_encoder.transform([flag])[0]
        except ValueError:
            encoded_flag = self.flag_encoder.transform([TCPState.OTH])[0]

        features = np.array([encoded_service, encoded_flag, src_bytes, dst_bytes])
        return features

    def _process_batch(self):
        if not self.batch_data:
            return

        features_list, metadata_list = zip(*self.batch_data)
        batch = np.array(features_list)
        batch_scaled = scaler.transform(batch)

        predictions = self._get_predictions(batch_scaled)

        for prediction, probability, features, metadata in zip(joblib_predictions, 
            joblib_probabilities, joblib_batch_scaled, metadata_list):
            logging.info(
                f"Prediction: {prediction}, Probability: {probability:.4f}, Features: {features.tolist()}, Metadata: {metadata}"
            )

        self.batch_data.clear()

    def _get_predictions(self, batch_scaled):
        if self.is_autoencoder:
            batch_reshaped = batch_scaled.reshape((
                batch_scaled.shape[0], 
                batch_scaled.shape[1], 
                1
            ))
            encoded_features = self.encoder.predict(batch_reshaped)
            reshaped_batch = encoded_features.reshape((
                encoded_features.shape[0], 
                -1
            ))

        if not self.is_ml_model and not self.is_autoencoder:
            reshaped_batch = batch_scaled.reshape((
                batch.shape[0], 
                batch.shape[1], 
                1
            ))
            probabilities = self.model.predict(reshaped_batch).flatten() 
        else:        
            probabilities = self.model.predict(encoded_features_flat) 

        return (probabilities >= self.probability_ratio).astype(int)