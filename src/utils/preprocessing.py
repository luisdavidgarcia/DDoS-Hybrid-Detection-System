import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

def preprocess_data(df):
    df.drop_duplicates(inplace=True)
    df.replace([np.inf, np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

def split_train_test_data(df, target_column, test_size=0.2):
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    return X_train, X_test, y_train, y_test

def scale_X_train_test_data(X_train, X_test, numerical_features=None, categorical_features=None):
    transformers = []

    if numerical_features is None and categorical_features is None:
        print("No features to scale or encode")
        return
    
    if numerical_features is not None:
        numerical_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        transformers.append(('num', numerical_transformer, numerical_features))
        
    if categorical_features is not None:
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])
        transformers.append(('cat', categorical_transformer, categorical_features))
        
    preprocessor = ColumnTransformer(transformers=transformers)

    X_train_preprocessed = preprocessor.fit_transform(X_train)
    X_test_preprocessed = preprocessor.transform(X_test)

    return X_train_preprocessed, X_test_preprocessed, preprocessor

def encode_y_train_test_data(y_train, y_test):
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)

    return y_train_encoded, y_test_encoded, le

