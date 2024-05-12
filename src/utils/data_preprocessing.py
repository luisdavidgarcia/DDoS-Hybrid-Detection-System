import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def prepare_norm_balanced_data(df, top_features=[], random_state=42, test_size=0.25, remove_duplicates=True, modify_inplace=True):
    """ Prepares the data for training and testing.

    Args:
        df: pandas DataFrame.
        top_features: List of top features to select.
        random_state: int, default=42.
        test_size: float, default=0.25.
        remove_duplicates: bool, default=True.
        modify_inplace: bool, default=False. If True, modifies the DataFrame in-place.

    Returns:
        x_train_scaled: pandas DataFrame (scaled training data).
        x_test_scaled: pandas DataFrame (scaled testing data).
        y_train: pandas Series (training labels).
        y_test: pandas Series (testing labels).
        label_mapping: dict (label encoding mapping).
    """

    if not modify_inplace:
        df = df.copy() 

    # Data Cleaning
    if remove_duplicates:
        df.drop_duplicates(keep='first', inplace=True)

    # df.dropna(subset=['Label'], inplace=True) 
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # Columns to Remove 
    cols_to_drop = ['Timestamp'] + df.columns[df.nunique() == 1].tolist()
    df.drop(columns=cols_to_drop, inplace=True) 

    # Get only the benign data, and drop the label column
    benign_rows = df[df['Label'] == 'Benign']
    benign_rows = benign_rows.drop(columns=['Label'])

    # Normalization and Split
    x_train, x_test = train_test_split(benign_rows, test_size=test_size, random_state=random_state)

    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    return pd.DataFrame(x_train_scaled, columns=x_train.columns, index=x_train.index), \
        pd.DataFrame(x_test_scaled, columns=x_test.columns, index=x_test.index)
