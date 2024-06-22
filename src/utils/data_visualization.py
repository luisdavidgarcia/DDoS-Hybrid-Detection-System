import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def plot_top_features(top_features, X_train):
    # top_features is a SelectKBest object
    mask = top_features.get_support()
    feature_scores = top_features.scores_

    selected_features = X_train.columns[mask]
    selected_scores = feature_scores[mask]

    df_top_features =  pd.DataFrame({
        'Feature': selected_features, 
        'Score': selected_scores
    })

    df_top_features = df_top_features.sort_values(by='Score', ascending=False)

    num_features = len(selected_features)
    plt.figure(figsize=(10, 5))
    plt.barh(df_top_features['Feature'], df_top_features['Score'])
    plt.xlabel('Mutual Information Score')
    plt.ylabel('Feature')
    plt.title(f'Top {num_features} Features')
    plt.gca().invert_yaxis()
    plt.show()

def plot_heatmap_correlation(df):
    plt.figure(figsize=(16, 10))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
