import re
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

legitimate_ips = {'172.19.5.12', '172.19.5.13'}
attack_ips = {'172.19.5.3', '172.19.5.4', '172.19.5.5'}

predictions_by_ip = defaultdict(lambda: {"0": 0, "1": 0})
outliers = {"0": 0, "1": 0}

prediction_pattern = re.compile(r"Prediction: (\d)")
src_ip_pattern = re.compile(r"'src_ip': '([\d\.]+)'")

model_name = "AE-XGBoost" 
path_to_log_file = f"/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/models/ae_xgb/ae_xgb_model_binary_predictions.log"

with open(path_to_log_file, "r") as log_data:
    for line in log_data.readlines():
        if "INFO" in line:
            prediction_match = prediction_pattern.search(line)
            src_ip_match = src_ip_pattern.search(line)
            
            if prediction_match and src_ip_match:
                prediction = prediction_match.group(1)
                src_ip = src_ip_match.group(1)
                
                if src_ip in legitimate_ips or src_ip in attack_ips:
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

conf_matrix = np.array([[TN, FP],
                        [FN, TP]])

plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal (0)', 'Attack (1)'], yticklabels=['Normal (0)', 'Attack (1)'])
plt.title(f'Confusion Matrix - {model_name}')
plt.xlabel('Predicted')
plt.ylabel('Actual')

fig, ax = plt.subplots(figsize=(6, 4))
cax = ax.matshow(conf_matrix, cmap='Blues')

plt.colorbar(cax)

for (i, j), val in np.ndenumerate(conf_matrix):
    color = 'white' if val > 2000 else 'black'  # Choose white text for dark cells and black for light cells
    ax.text(j, i, f'{val}', ha='center', va='center', color=color)

ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title(f'Confusion Matrix - {model_name}')

ax.xaxis.set_label_position('bottom')  
ax.xaxis.set_ticks_position('bottom')  
ax.set_xticklabels(['', 'Normal (0)', 'Attack (1)'])
ax.set_yticklabels(['', 'Normal (0)', 'Attack (1)'])

plt.savefig(f'{model_name}_confusion_matrix.png')

# ---- Plot Bar Charts for Each IP ----
# Separate IP addresses and prediction counts for plotting

ordered_ips = ['172.19.5.12', '172.19.5.13', '172.19.5.3', '172.19.5.4', '172.19.5.5']

ips = [ip for ip in ordered_ips if ip in predictions_by_ip]

pred_zeros = [predictions_by_ip[ip]["0"] for ip in ips]
pred_ones = [predictions_by_ip[ip]["1"] for ip in ips]

x = np.arange(len(ips))

plt.figure(figsize=(10, 6))
bars_zero = plt.bar(x - 0.2, pred_zeros, 0.4, label='Prediction 0', hatch='//')
bars_one = plt.bar(x + 0.2, pred_ones, 0.4, label='Prediction 1', hatch='\\')

for bar in bars_zero:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 50, int(yval), ha='center', va='bottom')  # ha: horizontal alignment

for bar in bars_one:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 50, int(yval), ha='center', va='bottom')

plt.xticks(x, ips)
plt.xlabel('IP Address')
plt.ylabel('Number of Predictions')
plt.title('Predictions by IP Address for Different Models')
plt.legend()

plt.savefig(f'{model_name}_predictions_by_ip.png')

plt.close()