import pandas as pd
import numpy as np
import os
import json
import time

def standardize_container_names(docker_stats_data):
    name_mapping = {
        'attacker1': 'attacker_syn',
        'attacker2': 'attacker_udp'
    }
    docker_stats_data['Container Name'] = \
        docker_stats_data['Container Name'].replace(name_mapping)
    return docker_stats_data

def parse_memory_values(memory_str):
    used, total = memory_str.split(' / ')
    
    def to_mib(mem):
        value = float(mem.rstrip('MiB GiB KiB K'))
        if 'GiB' in mem:
            return value * 1024
        elif 'KiB' in mem or 'K' in mem:
            return value / 1024
        elif 'MiB' not in mem:
            return value / (1024 * 1024)
        return value

    return to_mib(used), to_mib(total)

def parse_network_values(net_str):
    value = float(net_str.rstrip('kB MB GB B'))
    if 'MB' in net_str:
        return value * 1024
    elif 'GB' in net_str:
        return value * 1024 * 1024
    elif 'B' in net_str and 'kB' not in net_str and \
         'MB' not in net_str and 'GB' not in net_str:
        return value / 1024
    return value

def process_network_io(docker_stats_data):
    docker_stats_data[['Net I/O Received', 'Net I/O Sent']] = \
        docker_stats_data['Net I/O'].str.split(' / ', expand=True)
    
    docker_stats_data['Net I/O Received'] = \
        docker_stats_data['Net I/O Received'].apply(parse_network_values)
    docker_stats_data['Net I/O Sent'] = \
        docker_stats_data['Net I/O Sent'].apply(parse_network_values)
    
    docker_stats_data['Net I/O Received Rate'] = \
        docker_stats_data.groupby('Container Name')['Net I/O Received'].diff().fillna(0)
    docker_stats_data['Net I/O Sent Rate'] = \
        docker_stats_data.groupby('Container Name')['Net I/O Sent'].diff().fillna(0)
    
    return docker_stats_data

def calculate_container_metrics(container_data):
    metric_fields = {
        'CPU Usage (%)': container_data['CPU Usage (%)'],
        'Memory Usage (MiB)': container_data['Memory Usage'],
        'Net I/O Sent Rate (kB)': container_data['Net I/O Sent Rate'],
        'Net I/O Received Rate (kB)': container_data['Net I/O Received Rate']
    }
    
    metrics = {}
    for field_name, data in metric_fields.items():
        metrics[field_name] = {
            'Average': data.mean(),
            'Max': data.max(),
            'Min': data.min(),
            'Std Dev': data.std()
        }
    
    metrics['Cumulative Net I/O Sent (kB)'] = \
        container_data['Net I/O Sent'].iloc[-1]
    metrics['Cumulative Net I/O Received (kB)'] = \
        container_data['Net I/O Received'].iloc[-1]
    
    return metrics

def main():
    DOCKER_STATS_PATH = '../logs/docker_stats_20241001_221722.csv'
    docker_stats_data = pd.read_csv(DOCKER_STATS_PATH)
    docker_stats_data = standardize_container_names(docker_stats_data)
    
    docker_stats_data['CPU Usage (%)'] = \
        docker_stats_data['CPU Usage (%)'].str.rstrip('%').astype(float)
    
    docker_stats_data[['Memory Usage', 'Total Memory']] = \
        docker_stats_data['Memory Usage'].apply(
            lambda x: pd.Series(parse_memory_values(x))
        )
    
    docker_stats_data = process_network_io(docker_stats_data)
    
    metrics_summary = {
        container: calculate_container_metrics(
            docker_stats_data[docker_stats_data['Container Name'] == container]
        )
        for container in docker_stats_data['Container Name'].unique()
    }

    OPERATING_SYSTEM = 'windows'
    TIMESTAMP = time.strftime('%Y%m%d_%H%M%S')
    METRICS_DIR = '../logs/metrics'
    OUTPUT_FILENAME = f'docker_stats_summary_{OPERATING_SYSTEM}_{TIMESTAMP}.json'
    
    os.makedirs(METRICS_DIR, exist_ok=True)
    output_path = os.path.join(METRICS_DIR, OUTPUT_FILENAME)
    
    with open(output_path, 'w') as f:
        json.dump(metrics_summary, f, indent=4)

if __name__ == "__main__":
    main()