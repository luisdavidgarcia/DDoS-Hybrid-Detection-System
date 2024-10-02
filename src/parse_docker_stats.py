import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Read the CSV data into a DataFrame
csv_file_path = 'container_stats.csv'
df = pd.read_csv(csv_file_path)

# Clean up the percentage and memory usage columns for numerical operations
df['CPU Usage (%)'] = df['CPU Usage (%)'].str.rstrip('%').astype(float)
df['Memory Usage'] = df['Memory Usage'].apply(lambda x: float(x.split(' ')[0].rstrip('MiB')))
df[['Net I/O Sent', 'Net I/O Received']] = df['Net I/O'].str.split(' / ', expand=True)
df['Net I/O Sent'] = df['Net I/O Sent'].str.rstrip('kB').astype(float)
df['Net I/O Received'] = df['Net I/O Received'].str.rstrip('kB').astype(float)

# Convert the Timestamp column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# List of unique containers
containers = df['Container Name'].unique()

# Create subplots for each type of resource usage
fig, ax = plt.subplots(3, 1, figsize=(12, 18))

# Plot CPU usage
for container in containers:
    container_df = df[df['Container Name'] == container]
    ax[0].plot(container_df['Timestamp'], container_df['CPU Usage (%)'], marker='o', label=container)
ax[0].set_title('CPU Usage (%) Over Time')
ax[0].set_xlabel('Timestamp')
ax[0].set_ylabel('CPU Usage (%)')
ax[0].legend()
ax[0].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

# Plot Memory usage
for container in containers:
    container_df = df[df['Container Name'] == container]
    ax[1].plot(container_df['Timestamp'], container_df['Memory Usage'], marker='s', label=container)
ax[1].set_title('Memory Usage (MiB) Over Time')
ax[1].set_xlabel('Timestamp')
ax[1].set_ylabel('Memory Usage (MiB)')
ax[1].legend()
ax[1].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

# Plot Net I/O (Sent and Received)
for container in containers:
    container_df = df[df['Container Name'] == container]
    ax[2].plot(container_df['Timestamp'], container_df['Net I/O Sent'], marker='^', label=f'{container} - Sent')
    ax[2].plot(container_df['Timestamp'], container_df['Net I/O Received'], marker='v', label=f'{container} - Received')
ax[2].set_title('Network I/O (kB) Over Time')
ax[2].set_xlabel('Timestamp')
ax[2].set_ylabel('Net I/O (kB)')
ax[2].legend()
ax[2].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

# Adjust the layout and save the figure
plt.tight_layout()
plt.savefig('container_resource_usage.png')
plt.show()