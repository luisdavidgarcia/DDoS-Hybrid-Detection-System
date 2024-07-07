# src/utils/feature_engineering.py

from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def select_top_features(X_train, y_train, k, verbose=False):
    # mutual_info = mutual_info_classif(X_train, y_train)
    # mutual_info = pd.Series(mutual_info)
    # mutual_info.index = X_train.columns
    # mutual_info.sort_values(ascending=False, inplace=True)

    # if verbose:
    #     print(mutual_info)
    #     mutual_info.sort_values(ascending=False).plot.bar(figsize=(20, 10))

    top_features = SelectKBest(mutual_info_classif, k=k)
    top_features.fit(X_train, y_train)
    
    return top_features

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