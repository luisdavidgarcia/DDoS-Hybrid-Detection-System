import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import itertools
import os
import math

# Ensure the 'plots' directory exists
output_dir = 'docker_stats_plots_mac'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
# df[['Net I/O Sent', 'Net I/O Received']] = df['Net I/O'].str.split(' / ', expand=True)
# df['Net I/O Sent'] = df['Net I/O Sent'].apply(convert_net_io)
# df['Net I/O Received'] = df['Net I/O Received'].apply(convert_net_io)

df[['Net I/O Received', 'Net I/O Sent']] = df['Net I/O'].str.split(' / ', expand=True)
df['Net I/O Received'] = df['Net I/O Received'].apply(convert_net_io)
df['Net I/O Sent'] = df['Net I/O Sent'].apply(convert_net_io)

# Convert the Timestamp column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Find global min and max for CPU, Memory, and Net I/O across all containers
cpu_min, cpu_max = df['CPU Usage (%)'].min(), df['CPU Usage (%)'].max()
mem_min, mem_max = df['Memory Usage'].min(), df['Memory Usage'].max()
net_io_sent_min, net_io_sent_max = df['Net I/O Sent'].min(), df['Net I/O Sent'].max()
net_io_received_min, net_io_received_max = df['Net I/O Received'].min(), df['Net I/O Received'].max()

# Find global min and max for CPU, Memory, and Net I/O across all containers
cpu_min, cpu_max = df['CPU Usage (%)'].min(), df['CPU Usage (%)'].max()
mem_min, mem_max = df['Memory Usage'].min(), df['Memory Usage'].max()
net_io_sent_min, net_io_sent_max = df['Net I/O Sent'].min(), df['Net I/O Sent'].max()
net_io_received_min, net_io_received_max = df['Net I/O Received'].min(), df['Net I/O Received'].max()

# Round max values to the next higher number as per your request
# cpu_max = math.ceil(cpu_max / 10) * 10  # Round CPU to the next 10% (i.e., 90%)
# mem_max = math.ceil(mem_max / 100) * 100  # Round Memory to the next 100 MiB (i.e., 300 MiB)
# net_io_max = math.ceil(max(net_io_sent_max, net_io_received_max) / 100000) * 100000  # Round Net I/O to the next 100000 kB (i.e., 300000 kB)

cpu_max = 120
mem_max = 300
net_io_max = 300000

# List of unique containers
containers = df['Container Name'].unique()

# List of different marker shapes for each plot
cpu_markers = itertools.cycle(('o', 's', 'D', '^', 'v'))
memory_markers = itertools.cycle(('<', '>', 'p', '*', 'h'))
netio_markers = itertools.cycle(('x', 'P', 'H', '8', '+'))

# Create separate files for CPU, Memory, and Net I/O plots for each container
for container in containers:
    container_df = df[df['Container Name'] == container]

    # --- Plot CPU Usage ---
    plt.figure(figsize=(8, 6))
    plt.plot(container_df['Timestamp'], container_df['CPU Usage (%)'], marker=next(cpu_markers), markersize=4, label=container)
    plt.title(f'CPU Usage (%) for {container}')
    plt.xlabel('Timestamp')
    plt.ylabel('CPU Usage (%)')
    plt.ylim(cpu_min, cpu_max)  # Set the same y-axis range for all CPU plots
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{container}_cpu_usage.png'))
    plt.close()

    # --- Plot Memory Usage ---
    plt.figure(figsize=(8, 6))
    plt.plot(container_df['Timestamp'], container_df['Memory Usage'], marker=next(memory_markers), markersize=4, label=container)
    plt.title(f'Memory Usage (MiB) for {container}')
    plt.xlabel('Timestamp')
    plt.ylabel('Memory Usage (MiB)')
    plt.ylim(mem_min, mem_max)  # Set the same y-axis range for all Memory plots
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{container}_memory_usage.png'))
    plt.close()

    # --- Plot Net I/O ---
    plt.figure(figsize=(8, 6))
    plt.plot(container_df['Timestamp'], container_df['Net I/O Sent'], marker=next(netio_markers), markersize=4, label=f'{container} - Sent')
    plt.plot(container_df['Timestamp'], container_df['Net I/O Received'], marker=next(netio_markers), markersize=4, label=f'{container} - Received')
    plt.title(f'Network I/O (kB) for {container}')
    plt.xlabel('Timestamp')
    plt.ylabel('Net I/O (kB)')
    plt.ylim(min(net_io_sent_min, net_io_received_min), max(net_io_sent_max, net_io_received_max))  # Set the same y-axis range for all Net I/O plots
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.legend(loc='center right', ncol=1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{container}_net_io.png'))
    plt.close()