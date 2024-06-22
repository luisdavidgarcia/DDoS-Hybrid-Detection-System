from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest

import pandas as pd

def select_top_features(X_train, y_train, k, verbose=False):
    mutual_info = mutual_info_classif(X_train, y_train)
    mutual_info = pd.Series(mutual_info)
    mutual_info.index = X_train.columns
    mutual_info.sort_values(ascending=False, inplace=True)

    if verbose:
        print(mutual_info)
        mutual_info.sort_values(ascending=False).plot.bar(figsize=(20, 10))

    top_features = SelectKBest(mutual_info_classif, k=k)
    top_features.fit(X_train, y_train)
    
    return top_features