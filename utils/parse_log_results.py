import re
from collections import defaultdict
import ipaddress
import os
from datetime import datetime
import json

# Initialize dictionaries to track feature occurrences by IP
feature_occurrences_by_ip = defaultdict(lambda: {
    "src_bytes": defaultdict(int),
    "dst_bytes": defaultdict(int),
    "service": defaultdict(int),
    "flag": defaultdict(int),
    "predictions": defaultdict(int)
})

# Regular expression patterns for extracting necessary information
prediction_pattern = re.compile(r"Prediction: (\d)")
src_ip_pattern = re.compile(r"'src_ip': '([\d\.]+)'")
service_pattern = re.compile(r"'service': '(\w+)'")
flag_pattern = re.compile(r"'flag': '(\w+)'")
src_bytes_pattern = re.compile(r"'src_bytes': (\d+)")
dst_bytes_pattern = re.compile(r"'dst_bytes': (\d+)")

# Direct paths for saving results and log files (you can define these accordingly)
windows_path_to_save_results = "."
mac_path_to_log_file = ["/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/cnn_lstm_binary_model_predictions.log"]

# Define ground truth IP sets based on your specifications
server_ip = "172.19.5.2"  # Exclude this IP from analysis
attack_ips = {f"172.19.5.{i}" for i in range(3, 7)}  # Attackers: 172.19.5.3 - 172.19.5.6
legitimate_ips = {f"172.19.5.{i}" for i in range(7, 9)}  # Legitimate: 172.19.5.7 - 172.19.5.8

# Function to process log files and collect data
def process_log_file(path_to_log_file):
    with open(path_to_log_file, "r") as log_data:
        for line in log_data:
            if "INFO" in line:
                # Extract prediction and src_ip
                prediction_match = prediction_pattern.search(line)
                src_ip_match = src_ip_pattern.search(line)

                if prediction_match and src_ip_match:
                    prediction = prediction_match.group(1)
                    src_ip = src_ip_match.group(1)

                    try:
                        # Check if src_ip is a valid IPv4 address
                        ipaddress.IPv4Address(src_ip)
                    except ipaddress.AddressValueError:
                        continue  # Skip invalid IP addresses

                    # Exclude server IP from analysis
                    if src_ip == server_ip or src_ip == "172.19.5.1":
                        continue

                    # Extract additional feature information from the line
                    service_match = service_pattern.search(line)
                    flag_match = flag_pattern.search(line)
                    src_bytes_match = src_bytes_pattern.search(line)
                    dst_bytes_match = dst_bytes_pattern.search(line)

                    # Store the extracted feature data into the dictionary
                    if service_match:
                        service = service_match.group(1)
                        feature_occurrences_by_ip[src_ip]["service"][service] += 1

                    if flag_match:
                        flag = flag_match.group(1)
                        feature_occurrences_by_ip[src_ip]["flag"][flag] += 1

                    if src_bytes_match:
                        src_bytes = int(src_bytes_match.group(1))
                        feature_occurrences_by_ip[src_ip]["src_bytes"][src_bytes] += 1

                    if dst_bytes_match:
                        dst_bytes = int(dst_bytes_match.group(1))
                        feature_occurrences_by_ip[src_ip]["dst_bytes"][dst_bytes] += 1

                    # Update predictions count
                    feature_occurrences_by_ip[src_ip]["predictions"][prediction] += 1

# Process the log files for each model
for log_file in mac_path_to_log_file:
    process_log_file(log_file)

# Print results (You could write this to a file or visualize it)
for src_ip, data in feature_occurrences_by_ip.items():
    print(f"Source IP: {src_ip}")
    print(f"  Predictions: {dict(data['predictions'])}")
    print(f"  Src Bytes: {dict(data['src_bytes'])}")
    print(f"  Dst Bytes: {dict(data['dst_bytes'])}")
    print(f"  Service: {dict(data['service'])}")
    print(f"  Flags: {dict(data['flag'])}")
    print()

# Optionally, you can save the results to a JSON file
output_file = os.path.join(windows_path_to_save_results, f"feature_analysis_linux.json")
with open(output_file, "w") as f:
    json.dump(feature_occurrences_by_ip, f, indent=4)