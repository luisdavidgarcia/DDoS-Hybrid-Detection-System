import re
import json
import os
import ipaddress
from collections import defaultdict
from datetime import datetime

def create_regex_patterns():
    return {
        'prediction': re.compile(r"Prediction: (\d)"),
        'src_ip': re.compile(r"'src_ip': '([\d\.]+)'"),
        'service': re.compile(r"'service': '(\w+)'"),
        'flag': re.compile(r"'flag': '(\w+)'"),
        'src_bytes': re.compile(r"'src_bytes': (\d+)"),
        'dst_bytes': re.compile(r"'dst_bytes': (\d+)")
    }

def create_ip_feature_tracker():
    return defaultdict(lambda: {
        "src_bytes": defaultdict(int),
        "dst_bytes": defaultdict(int),
        "service": defaultdict(int),
        "flag": defaultdict(int),
        "predictions": defaultdict(int)
    })

def is_valid_ip(ip_address, excluded_ips):
    try:
        ipaddress.IPv4Address(ip_address)
        return ip_address not in excluded_ips
    except ipaddress.AddressValueError:
        return False

def extract_features(line, patterns, feature_tracker, excluded_ips):
    if "INFO" not in line:
        return

    prediction_match = patterns['prediction'].search(line)
    src_ip_match = patterns['src_ip'].search(line)

    if not (prediction_match and src_ip_match):
        return

    src_ip = src_ip_match.group(1)
    if not is_valid_ip(src_ip, excluded_ips):
        return

    prediction = prediction_match.group(1)
    feature_tracker[src_ip]["predictions"][prediction] += 1

    feature_matches = {
        'service': (patterns['service'], "service"),
        'flag': (patterns['flag'], "flag"),
        'src_bytes': (patterns['src_bytes'], "src_bytes"),
        'dst_bytes': (patterns['dst_bytes'], "dst_bytes")
    }

    for feature, (pattern, key) in feature_matches.items():
        match = pattern.search(line)
        if match:
            value = match.group(1)
            if 'bytes' in feature:
                value = int(value)
            feature_tracker[src_ip][key][value] += 1

def process_log_file(log_path, patterns, feature_tracker, excluded_ips):
    with open(log_path, "r") as log_data:
        for line in log_data:
            extract_features(line, patterns, feature_tracker, excluded_ips)

def save_results(feature_tracker, output_path):
    with open(output_path, "w") as f:
        json.dump(feature_tracker, f, indent=4)

def print_analysis(feature_tracker):
    for src_ip, data in feature_tracker.items():
        print(f"Source IP: {src_ip}")
        print(f"  Predictions: {dict(data['predictions'])}")
        print(f"  Src Bytes: {dict(data['src_bytes'])}")
        print(f"  Dst Bytes: {dict(data['dst_bytes'])}")
        print(f"  Service: {dict(data['service'])}")
        print(f"  Flags: {dict(data['flag'])}")
        print()

def main():
    LOG_PATH = "../logs/cnn_lstm_predictions.log"
    OUTPUT_DIR = "."
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILENAME = f"feature_analysis_{TIMESTAMP}.json"
    
    EXCLUDED_IPS = {"172.19.5.1", "172.19.5.2"}

    patterns = create_regex_patterns()
    feature_tracker = create_ip_feature_tracker()
    
    process_log_file(LOG_PATH, patterns, feature_tracker, EXCLUDED_IPS)
    
    print_analysis(feature_tracker)
    
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    save_results(feature_tracker, output_path)

if __name__ == "__main__":
    main()