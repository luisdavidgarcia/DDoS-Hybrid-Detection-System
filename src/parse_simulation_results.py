import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Updated IP sets
legitimate_ips = {
    '172.19.5.12',  # legit_http
    '172.19.5.13',  # legit_https
    '172.19.5.14',  # legit_ftp
    '172.19.5.15',  # legit_ssh
    '172.19.5.16',  # legit_dns
    '172.19.5.17',  # legit_smtp
    '172.19.5.18',  # legit_pop3
    '172.19.5.19'   # legit_imap
}

attack_ips = {
    '172.19.5.3',   # attacker1
    '172.19.5.4',   # attacker2
    '172.19.5.5',   # attacker3
    '172.19.5.20',  # neptune_attack
    '172.19.5.21',  # smurf_attack
    '172.19.5.22',  # pod_attack
    '172.19.5.23'   # udpstorm_attack
}
server_ips = {'172.19.5.2'}  # nginx_web server

predictions_by_ip = defaultdict(lambda: {"0": 0, "1": 0})
outliers = {"0": 0, "1": 0}

prediction_pattern = re.compile(r"Prediction: (\d)")
src_ip_pattern = re.compile(r"'src_ip': '([\d\.]+)'")

model_name = "CNN-LSTM"
path_to_log_file = f"/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/models/cnn_lstm/cnn_lstm_model_binary_predictions.log"

with open(path_to_log_file, "r") as log_data:
    for line in log_data.readlines():
        if "INFO" in line:
            prediction_match = prediction_pattern.search(line)
            src_ip_match = src_ip_pattern.search(line)
            
            if prediction_match and src_ip_match:
                prediction = prediction_match.group(1)
                src_ip = src_ip_match.group(1)
                
                if src_ip in legitimate_ips or src_ip in attack_ips or src_ip in server_ips:
                    predictions_by_ip[src_ip][prediction] += 1
                else:
                    outliers[prediction] += 1

TP, FP, TN, FN = 0, 0, 0, 0

for ip, counts in predictions_by_ip.items():
    if ip in legitimate_ips:
        TN += counts['0']
        FP += counts['1']
    elif ip in attack_ips:
        TP += counts['1']
        FN += counts['0']

def calculate_metrics(tp, tn, fp, fn):
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) != 0 else 0
    precision = tp / (tp + fp) if (tp + fp) != 0 else 0
    recall = tp / (tp + fn) if (tp + fn) != 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    return accuracy, precision, recall, f1_score

accuracy, precision, recall, f1_score = calculate_metrics(TP, TN, FP, FN)

print(f"\nMetrics for {path_to_log_file}:")
print(f"True Positives (TP): {TP}")
print(f"False Positives (FP): {FP}")
print(f"True Negatives (TN): {TN}")
print(f"False Negatives (FN): {FN}")
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1_score}")

print(f"\nOutliers, Prediction 0: {outliers['0']}, Prediction 1: {outliers['1']}")

# Plotting Confusion Matrix
plt.figure(figsize=(6, 4))
sns.heatmap(np.array([[TN, FP], [FN, TP]]), annot=True, fmt='d', cmap='Blues',
            xticklabels=['Normal (0)', 'Attack (1)'], yticklabels=['Normal (0)', 'Attack (1)'])
plt.title(f'Confusion Matrix - {model_name}')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# Plot Bar Charts for Each IP
ordered_ips = sorted(list(predictions_by_ip.keys()), key=lambda x: int(x.split('.')[-1]))  # Sorting IPs by the last octet
pred_zeros = [predictions_by_ip[ip]["0"] for ip in ordered_ips]
pred_ones = [predictions_by_ip[ip]["1"] for ip in ordered_ips]

x = np.arange(len(ordered_ips))

plt.figure(figsize=(10, 6))
bars_zero = plt.bar(x - 0.2, pred_zeros, 0.4, label='Normal', hatch='//')
bars_one = plt.bar(x + 0.2, pred_ones, 0.4, label='Attack', hatch='\\')

plt.ylim(0, max(pred_zeros + pred_ones) + 10)  # Adjusting vertical axis to fit labels

for bar in bars_zero + bars_one:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval)}', ha='center', va='bottom')

plt.xticks(x, ordered_ips, rotation=45)  # Tilting x-axis labels for better visibility
plt.xlabel('IP Address')
plt.ylabel('Number of Predictions')
plt.title(f'Predictions by IP Address for {model_name}')
plt.legend()
plt.tight_layout()
plt.show()