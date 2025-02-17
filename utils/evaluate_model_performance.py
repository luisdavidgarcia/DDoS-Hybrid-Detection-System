import re
import os
import numpy as np
import matplotlib.pyplot as plt
import ipaddress
from collections import defaultdict
from datetime import datetime

def create_regex_patterns():
    return {
        'prediction': re.compile(r"Prediction: (\d)"),
        'src_ip': re.compile(r"'src_ip': '([\d\.]+)'")
    }

def is_valid_ip(ip_address, excluded_ips):
    try:
        ipaddress.IPv4Address(ip_address)
        return ip_address not in excluded_ips
    except ipaddress.AddressValueError:
        return False

def process_predictions(log_path, patterns, excluded_ips):
    predictions = defaultdict(lambda: {"0": 0, "1": 0})
    
    with open(log_path, "r") as log_data:
        for line in log_data:
            if "INFO" not in line:
                continue

            prediction_match = patterns['prediction'].search(line)
            src_ip_match = patterns['src_ip'].search(line)

            if prediction_match and src_ip_match:
                prediction = prediction_match.group(1)
                src_ip = src_ip_match.group(1)

                if is_valid_ip(src_ip, excluded_ips):
                    predictions[src_ip][prediction] += 1
                    
    return predictions

def calculate_metrics(predictions, legitimate_ips, attack_ips):
    tp = tn = fp = fn = 0

    for ip, counts in predictions.items():
        if ip in legitimate_ips:
            tn += counts['0']
            fp += counts['1']
        elif ip in attack_ips:
            fn += counts['0']
            tp += counts['1']
    
    total = tp + tn + fp + fn
    
    metrics = {
        'confusion_matrix': (tp, tn, fp, fn),
        'accuracy': (tp + tn) / total if total else 0,
        'precision': tp / (tp + fp) if (tp + fp) else 0,
        'recall': tp / (tp + fn) if (tp + fn) else 0
    }
    
    metrics['f1_score'] = 2 * (metrics['precision'] * metrics['recall']) / \
        (metrics['precision'] + metrics['recall']) \
        if (metrics['precision'] + metrics['recall']) else 0
        
    return metrics

def save_results(save_dir, model_name, timestamp, predictions, metrics):
    os.makedirs(save_dir, exist_ok=True)
    
    results_path = os.path.join(save_dir, f"{model_name}_results_{timestamp}.txt")
    plot_path = os.path.join(save_dir, f"{model_name}_predictions_{timestamp}.png")
    
    tp, tn, fp, fn = metrics['confusion_matrix']
    
    with open(results_path, "w") as f:
        f.write(f"Results for {model_name}:\n\n")
        f.write("Total Predictions:\n")
        f.write(f"Normal (0): {tn + fn}\n")
        f.write(f"Attack (1): {tp + fp}\n\n")
        
        f.write("Performance Metrics:\n")
        f.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
        f.write(f"Precision: {metrics['precision']:.4f}\n")
        f.write(f"Recall: {metrics['recall']:.4f}\n")
        f.write(f"F1 Score: {metrics['f1_score']:.4f}\n\n")
        
        f.write("Predictions by IP:\n")
        for ip in sorted(predictions.keys(), 
                        key=lambda x: [int(p) for p in x.split('.')]):
            counts = predictions[ip]
            f.write(f"IP: {ip}, Normal: {counts['0']}, Attack: {counts['1']}\n")
        
        f.write("\nConfusion Matrix:\n")
        f.write(f"[{tn} {fp}]\n[{fn} {tp}]\n")
    
    plot_predictions(predictions, model_name, plot_path)

def plot_predictions(predictions, model_name, plot_path):
    ordered_ips = sorted(predictions.keys(), 
                        key=lambda x: [int(p) for p in x.split('.')])
    
    pred_zeros = [predictions[ip]["0"] for ip in ordered_ips]
    pred_ones = [predictions[ip]["1"] for ip in ordered_ips]
    max_height = max(max(pred_zeros), max(pred_ones))
    
    plt.figure(figsize=(7, 5))
    x = np.arange(len(ordered_ips))
    
    bars_normal = plt.bar(x - 0.2, pred_zeros, 0.4, 
                         label='Normal (0)', hatch='//')
    bars_attack = plt.bar(x + 0.2, pred_ones, 0.4, 
                         label='Attack (1)', hatch='\\')
    
    for bars in [bars_normal, bars_attack]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2, height + 1,
                        f'{int(height)}', ha='center', va='bottom')
    
    plt.ylim(0, max_height + max_height * 0.1)  # Add 10% padding
    plt.xticks(x, ordered_ips, rotation=45)
    plt.xlabel('IP Address')
    plt.ylabel('Number of Predictions')
    plt.title(f'Predictions by IP Address for {model_name}')
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(plot_path)
    plt.close()

def main():
    EXCLUDED_IPS = {"172.19.5.1", "172.19.5.2"}
    ATTACK_IPS = {f"172.19.5.{i}" for i in range(3, 7)}
    LEGITIMATE_IPS = {f"172.19.5.{i}" for i in range(7, 9)}
    
    MODEL_CONFIGS = [
        ("cnn_lstm", "CNN-LSTM"),
        ("ae_xgb", "AE-XGBoost"),
        ("xgb", "XGBoost"),
        ("lr", "Logistic_Regression"),
        ("rf", "Random_Forest"),
        ("dt", "Decision_Tree")
    ]
    
    OPERATING_SYSTEM = 'windows'
    BASE_DIR = "../models"
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    patterns = create_regex_patterns()
    
    for model_dir, model_name in MODEL_CONFIGS:
        log_path = os.path.join(BASE_DIR, model_dir, 
                                f"{model_dir}_predictions.log")
        save_dir = os.path.join(BASE_DIR, model_dir, 
                                f"results_{platform}")
        
        predictions = process_predictions(log_path, patterns, EXCLUDED_IPS)
        
        metrics = calculate_metrics(predictions, LEGITIMATE_IPS, ATTACK_IPS)
        
        save_results(save_dir, model_name, TIMESTAMP, predictions, metrics)

if __name__ == "__main__":
    main()