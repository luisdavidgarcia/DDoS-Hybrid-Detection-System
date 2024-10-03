import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import ipaddress
import os
from datetime import datetime

# Initialize the predictions_by_ip dictionary
predictions_by_ip = defaultdict(lambda: {"0": 0, "1": 0})

# Pattern matching for prediction and src_ip
prediction_pattern = re.compile(r"Prediction: (\d)")
src_ip_pattern = re.compile(r"'src_ip': '([\d\.]+)'")

# Direct paths for saving results and log files
windows_path_to_save_results = "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/model_results"
windows_path_to_log_file = [
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/cnn_lstm_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/ae_xgb_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/xgboost_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/logistic_regression_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/random_forest_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_windows_10-02-2024/decision_tree_binary_model_predictions.log"
]

linux_path_to_save_results = "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/model_results/"
linux_path_to_log_file = [
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/cnn_lstm_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/ae_xgb_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/xgboost_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/logistic_regression_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/random_forest_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_linux_10-02-2024/decision_tree_binary_model_predictions.log"
]

mac_path_to_save_results = "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/model_results/"
mac_path_to_log_file = [
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/cnn_lstm_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/ae_xgb_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/xgboost_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/logistic_regression_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/random_forest_binary_model_predictions.log",
    "/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/decision_tree_binary_model_predictions.log"
]

# List of model names
model_names = ["CNN-LSTM", "AE-XGBoost", "XGBoost", "Logistic_Regression", "Random_Forest", "Decision_Tree"]

# Generate timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define ground truth IP sets based on your specifications
server_ip = "172.19.5.2"  # Exclude this IP from analysis

attack_ips = {f"172.19.5.{i}" for i in range(3, 7)}  # Attackers: 172.19.5.3 - 172.19.5.6
legitimate_ips = {f"172.19.5.{i}" for i in range(7, 9)}  # Legitimate: 172.19.5.7 - 172.19.5.8

# Read the log file and process each line
def process_log_file(path_to_log_file):
    with open(path_to_log_file, "r") as log_data:
        for line in log_data:
            if "INFO" in line:
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

                    # Update predictions_by_ip dictionary
                    predictions_by_ip[src_ip][prediction] += 1

# Now, we can process the predictions_by_ip to compute TP, FP, TN, FN
def calculate_metrics_by_ip():
    TP, FP, TN, FN = 0, 0, 0, 0

    for ip, counts in predictions_by_ip.items():
        actual_label = None
        if ip in legitimate_ips:
            actual_label = '0'  # Normal
        elif ip in attack_ips:
            actual_label = '1'  # Attack
        else:
            continue  # Ignore IPs that are neither in legitimate_ips nor attack_ips

        # Aggregate counts
        if actual_label == '0':
            TN += counts['0']
            FP += counts['1']
        elif actual_label == '1':
            FN += counts['0']
            TP += counts['1']

    return TP, TN, FP, FN

# Calculate final metrics
def calculate_final_metrics(tp, tn, fp, fn):
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) != 0 else 0
    precision = tp / (tp + fp) if (tp + fp) != 0 else 0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    return accuracy, precision, recall, f1_score

# Save results and plots to the respective paths
def save_results_to_path(path_to_save_results, model_name, timestamp, TP, TN, FP, FN, accuracy, precision, recall, f1_score):
    # Ensure the directory exists
    os.makedirs(path_to_save_results, exist_ok=True)
    
    # Create output filenames with model_name and timestamp
    results_txt_file = f"{model_name}_results_{timestamp}.txt"
    predictions_plot_filename = f"{model_name}_predictions_by_ip_{timestamp}.png"

    # Save the results to a text file
    with open(os.path.join(path_to_save_results, results_txt_file), "w") as f:
        f.write(f"Results for {model_name}:\n")
        f.write(f"Total Predictions:\n")
        f.write(f"Prediction 0 (Normal): {TN + FN}\n")
        f.write(f"Prediction 1 (Attack): {TP + FP}\n\n")
        f.write(f"Metrics:\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1 Score: {f1_score:.4f}\n\n")
        f.write("Predictions by IP:\n")
        for ip in sorted(predictions_by_ip.keys(), key=lambda x: [int(octet) for octet in x.split('.')]):
            counts = predictions_by_ip[ip]
            f.write(f"IP: {ip}, Prediction 0: {counts['0']}, Prediction 1: {counts['1']}\n")
        # Print confusion matrix nicely
        f.write(f"\nConfusion Matrix:\n")
        f.write(f"True Positives (Attack): {TP}\n")
        f.write(f"False Positives (Attack): {FP}\n")
        f.write(f"True Negatives (Normal): {TN}\n")
        f.write(f"False Negatives (Normal): {FN}\n\n")
        f.write(f"[{TN} {FP}]\n[{FN} {TP}]\n\n")

    print(f"Results saved to {os.path.join(path_to_save_results, results_txt_file)}")

    # Plotting Bar Chart for Predictions
    ordered_ips = sorted(predictions_by_ip.keys(), key=lambda x: [int(octet) for octet in x.split('.')])

    pred_zeros = [predictions_by_ip[ip]["0"] for ip in ordered_ips]
    pred_ones = [predictions_by_ip[ip]["1"] for ip in ordered_ips]

    x = np.arange(len(ordered_ips))

    plt.figure(figsize=(7, 5))
    bars_zero = plt.bar(x - 0.2, pred_zeros, 0.4, label='Prediction 0 (Normal)', hatch='//')
    bars_one = plt.bar(x + 0.2, pred_ones, 0.4, label='Prediction 1 (Attack)', hatch='\\')

    plt.ylim(0, max(pred_zeros + pred_ones) + 1000)  # Adjust vertical axis to fit labels

    for bar in bars_zero + bars_one:
        yval = bar.get_height()
        if yval > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 1, f'{int(yval)}', ha='center', va='bottom')

    plt.xticks(x, ordered_ips, rotation=45)  # Tilt x-axis labels for better visibility
    plt.xlabel('IP Address')
    plt.ylabel('Number of Predictions')
    plt.title(f'Predictions by IP Address for {model_name}')
    plt.legend()
    plt.tight_layout()

    # Save the predictions plot
    plt.savefig(os.path.join(path_to_save_results, predictions_plot_filename))
    print(f"Predictions plot saved to {os.path.join(path_to_save_results, predictions_plot_filename)}")

# Process log files for each model and save results for each platform
for i, model_name in enumerate(model_names):
    # Process log files
    process_log_file(windows_path_to_log_file[i])
    TP, TN, FP, FN = calculate_metrics_by_ip()
    accuracy, precision, recall, f1_score = calculate_final_metrics(TP, TN, FP, FN)
    save_results_to_path(windows_path_to_save_results, model_name, timestamp, TP, TN, FP, FN, accuracy, precision, recall, f1_score)

    process_log_file(linux_path_to_log_file[i])
    TP, TN, FP, FN = calculate_metrics_by_ip()
    accuracy, precision, recall, f1_score = calculate_final_metrics(TP, TN, FP, FN)
    save_results_to_path(linux_path_to_save_results, model_name, timestamp, TP, TN, FP, FN, accuracy, precision, recall, f1_score)

    process_log_file(mac_path_to_log_file[i])
    TP, TN, FP, FN = calculate_metrics_by_ip()
    accuracy, precision, recall, f1_score = calculate_final_metrics(TP, TN, FP, FN)
    save_results_to_path(mac_path_to_save_results, model_name, timestamp, TP, TN, FP, FN, accuracy, precision, recall, f1_score)