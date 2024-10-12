import pandas as pd
import numpy as np
import os
import json
import time

# Filename
operating_system = 'mac'
date_timestamp = time.strftime('%Y%m%d_%H%M%S')
filename = f'docker_stats_summary_{operating_system}_{date_timestamp}.json'

# Ensure the 'metrics' directory exists
metrics_dir = '/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024'
if not os.path.exists(metrics_dir):
    os.makedirs(metrics_dir)

# Read the CSV data into a DataFrame
csv_file_path = '/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/logs/scenario1_mac_10-01-2024/docker_stats_20241001_221722.csv'
df = pd.read_csv(csv_file_path)

# Replace attacker1 with attacker_syn and attacker2 with attacker_udp
df['Container Name'] = df['Container Name'].replace({'attacker1': 'attacker_syn', 'attacker2': 'attacker_udp'})

# Clean up the percentage columns for numerical operations
df['CPU Usage (%)'] = df['CPU Usage (%)'].str.rstrip('%').astype(float)

# Function to handle different memory units (parses both used memory and total memory)
def convert_memory_usage(mem_str):
    used_memory, total_memory = mem_str.split(' / ')
    
    def convert(mem):
        if 'MiB' in mem:
            return float(mem.rstrip('MiB'))  # MiB is the default unit
        elif 'GiB' in mem:
            return float(mem.rstrip('GiB')) * 1024  # Convert GiB to MiB
        elif 'KiB' in mem or 'K' in mem:
            return float(mem.rstrip('KiB')) / 1024  # Convert KiB to MiB
        else:
            return float(mem) / (1024 * 1024)  # Assume bytes if no unit

    return convert(used_memory), convert(total_memory)

# Apply the conversion function to the Memory Usage column (this handles both used and total memory)
df[['Memory Usage', 'Total Memory']] = df['Memory Usage'].apply(lambda x: pd.Series(convert_memory_usage(x)))

# Function to convert Net I/O units to kilobytes (kB)
def convert_net_io(net_io_str):
    if 'kB' in net_io_str:
        return float(net_io_str.rstrip('kB'))
    elif 'MB' in net_io_str:
        return float(net_io_str.rstrip('MB')) * 1024  # Convert MB to kB
    elif 'GB' in net_io_str:
        return float(net_io_str.rstrip('GB')) * 1024 * 1024  # Convert GB to kB
    elif 'B' in net_io_str:
        return float(net_io_str.rstrip('B')) / 1024  # Convert Bytes to kB
    else:
        return float(net_io_str)  # No unit specified, assume bytes and convert to kB

# Process Net I/O (handle both Sent and Received columns)
df[['Net I/O Sent', 'Net I/O Received']] = df['Net I/O'].str.split(' / ', expand=True)
df['Net I/O Sent'] = df['Net I/O Sent'].apply(convert_net_io)
df['Net I/O Received'] = df['Net I/O Received'].apply(convert_net_io)

# List of unique containers
containers = df['Container Name'].unique()

# Dictionary to store the summary metrics
metrics_summary = {}

# Iterate over each container to calculate summary statistics
for container in containers:
    container_df = df[df['Container Name'] == container]
    
    # Initialize a dictionary for each container's metrics
    metrics_summary[container] = {
        'CPU Usage (%)': {
            'Average': container_df['CPU Usage (%)'].mean(),
            'Max': container_df['CPU Usage (%)'].max(),
            'Min': container_df['CPU Usage (%)'].min(),
            'Std Dev': container_df['CPU Usage (%)'].std()
        },
        'Memory Usage (MiB)': {
            'Average': container_df['Memory Usage'].mean(),
            'Max': container_df['Memory Usage'].max(),
            'Min': container_df['Memory Usage'].min(),
            'Std Dev': container_df['Memory Usage'].std()
        },
        'Net I/O Sent (kB)': {
            'Average': container_df['Net I/O Sent'].mean(),
            'Max': container_df['Net I/O Sent'].max(),
            'Min': container_df['Net I/O Sent'].min(),
            'Std Dev': container_df['Net I/O Sent'].std()
        },
        'Net I/O Received (kB)': {
            'Average': container_df['Net I/O Received'].mean(),
            'Max': container_df['Net I/O Received'].max(),
            'Min': container_df['Net I/O Received'].min(),
            'Std Dev': container_df['Net I/O Received'].std()
        }
    }

# Save the metrics summary to a JSON file
metrics_summary_path = os.path.join(metrics_dir, filename)
with open(metrics_summary_path, 'w') as json_file:
    json.dump(metrics_summary, json_file, indent=4)

print(f"Summary metrics saved to {metrics_summary_path}")