import matplotlib.pyplot as plt

def data_preview(df):
    print("Data Frame Shape: ", df.shape)
    print("Data Frame Columns: ", df.columns)
    print("------------------------------------")
    print("Data Frame Head: ")
    print(df.head())
    print("------------------------------------")
    print("Data Frame Info: ")
    print(df.info())
    print("------------------------------------")

# Helper function to plot bar labels
def add_bar_labels(bars):
    # Add counts on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{height}',
            ha='center',
            va='bottom'
        )

def plot_label_distribution(df, target_column):
    label_counts = df[target_column].value_counts()
    print("Label Distribution: ")
    print(label_counts)
    print("------------------------------------")

    plt.figure(figsize=(10, 5))
    bars = plt.bar(label_counts.index, label_counts.values)
    add_bar_labels(bars)
    plt.xticks(rotation=45)
    plt.title("Target Label Distribution")
    plt.xlabel("Target Labels")
    plt.ylabel("Count")
    plt.show()
