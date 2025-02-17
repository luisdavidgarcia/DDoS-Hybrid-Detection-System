import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import itertools
import os

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

def preprocess_docker_stats(docker_stats_data):
    docker_stats_data['Container Name'] = \
        docker_stats_data['Container Name'].replace({
            'attacker1': 'attacker_syn', 
            'attacker2': 'attacker_udp'
        })
    
    docker_stats_data['CPU Usage (%)'] = \
        docker_stats_data['CPU Usage (%)'].str.rstrip('%').astype(float)
    
    docker_stats_data[['Memory Usage', 'Total Memory']] = \
        docker_stats_data['Memory Usage'].apply(lambda x: pd.Series(
            parse_memory_values(x)
        ))
    
    docker_stats_data[['Net I/O Received', 'Net I/O Sent']] = \
        docker_stats_data['Net I/O'].str.split(' / ', expand=True)
    
    docker_stats_data['Net I/O Received'] = \
        docker_stats_data['Net I/O Received'].apply(parse_network_values)
    docker_stats_data['Net I/O Sent'] = \
        docker_stats_data['Net I/O Sent'].apply(parse_network_values)
    
    docker_stats_data['Timestamp'] = pd.to_datetime(
        docker_stats_data['Timestamp']
    )
    
    return docker_stats_data

def plot_cpu_usage(container_data, output_path, marker, y_limits):
    plt.figure(figsize=(8, 6))
    plt.plot(
        container_data['Timestamp'],
        container_data['CPU Usage (%)'],
        marker=marker,
        markersize=4,
        label=container_data['Container Name'].iloc[0]
    )
    plt.title(f'CPU Usage (%) for {container_data["Container Name"].iloc[0]}')
    plt.xlabel('Timestamp')
    plt.ylabel('CPU Usage (%)')
    plt.ylim(*y_limits)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_memory_usage(container_data, output_path, marker, y_limits):
    plt.figure(figsize=(8, 6))
    plt.plot(
        container_data['Timestamp'],
        container_data['Memory Usage'],
        marker=marker,
        markersize=4,
        label=container_data['Container Name'].iloc[0]
    )
    plt.title(f'Memory Usage (MiB) for {container_data["Container Name"].iloc[0]}')
    plt.xlabel('Timestamp')
    plt.ylabel('Memory Usage (MiB)')
    plt.ylim(*y_limits)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_network_io(container_data, output_path, markers, y_limits):
    plt.figure(figsize=(8, 6))
    container_name = container_data['Container Name'].iloc[0]
    
    plt.plot(
        container_data['Timestamp'],
        container_data['Net I/O Sent'],
        marker=next(markers),
        markersize=4,
        label=f'{container_name} - Sent'
    )
    plt.plot(
        container_data['Timestamp'],
        container_data['Net I/O Received'],
        marker=next(markers),
        markersize=4,
        label=f'{container_name} - Received'
    )
    plt.title(f'Network I/O (kB) for {container_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Net I/O (kB)')
    plt.ylim(*y_limits)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.legend(loc='center right', ncol=1)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    DOCKER_STATS_PATH = '../logs/docker_stats_20241001_221722.csv'
    OUTPUT_DIR = 'docker_stats_plots_mac'
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    docker_stats_data = pd.read_csv(DOCKER_STATS_PATH)
    docker_stats_data = preprocess_docker_stats(docker_stats_data)
    
    MAX_CPU_PERCENTAGE = 120
    MAX_MEMORY_MIB = 300
    MAX_NETWORK_KB = 300000 
    y_limits = {
        'cpu': (docker_stats_data['CPU Usage (%)'].min(), MAX_CPU_PERCENTAGE),
        'memory': (docker_stats_data['Memory Usage'].min(), MAX_MEMORY_MIB),
        'network': (
            min(docker_stats_data['Net I/O Sent'].min(),
                docker_stats_data['Net I/O Received'].min()),
            MAX_NETWORK_KB
        )
    }
    
    markers = {
        'cpu': itertools.cycle(('o', 's', 'D', '^', 'v')),
        'memory': itertools.cycle(('<', '>', 'p', '*', 'h')),
        'network': itertools.cycle(('x', 'P', 'H', '8', '+'))
    }
    
    for container in docker_stats_data['Container Name'].unique():
        container_data = docker_stats_data[
            docker_stats_data['Container Name'] == container
        ]
        
        plot_cpu_usage(
            container_data,
            os.path.join(OUTPUT_DIR, f'{container}_cpu_usage.png'),
            next(markers['cpu']),
            y_limits['cpu']
        )
        
        plot_memory_usage(
            container_data,
            os.path.join(OUTPUT_DIR, f'{container}_memory_usage.png'),
            next(markers['memory']),
            y_limits['memory']
        )
        
        plot_network_io(
            container_data,
            os.path.join(OUTPUT_DIR, f'{container}_net_io.png'),
            markers['network'],
            y_limits['network']
        )

if __name__ == "__main__":
    main()