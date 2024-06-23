from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

import pandas as pd

from src.utils.data_visualization import data_preview

from src.utils.preprocessing import preprocess_data
from src.utils.preprocessing import split_train_test_data
from src.utils.preprocessing import scale_X_train_test_data
from src.utils.preprocessing import encode_y_train_test_data

from src.utils.feature_engineering import select_top_features

from src.utils.model_evaluation import decode_y
from src.utils.model_evaluation import train_model
from src.utils.model_evaluation import evaluate_model
from src.utils.model_evaluation import save_map_of_model_metrics

# Acquire the dataset
dataset_path = 'datasets/cic_ids_2018/combined.csv'
df = pd.read_csv(dataset_path)
data_preview(df)

# Preprocess the dataset
preprocess_data(df)
df.drop('Timestamp', axis=1, inplace=True)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = split_train_test_data(df, 'Label')

# Feature Engineering
top_features = select_top_features(X_train, y_train, k=10, verbose=True)
X_train_reduced = top_features.transform(X_train)
X_test_reduced = top_features.transform(X_test)

# Scaling and Encoding
X_train_scaled, X_test_scaled, scaler = scale_X_train_test_data(X_train_reduced, X_test_reduced, X_train.columns)

y_train_encoded, y_test_encoded, le = encode_y_train_test_data(y_train, y_test)

# Create the classifiers
models = {
    "XGBoost": XGBClassifier(
        objective='multi:softprob',
        num_class=len(le.classes_),
        eval_metric='mlogloss',
        use_label_encoder=False
    ),
    "Logistic Regression": LogisticRegression(max_iter=2000),
    "Random Forest": RandomForestClassifier(n_estimators=100),
    "Decision Tree": DecisionTreeClassifier(),
}

# Train and evaluate each model
results = {}

for name, model in models.items():
    model, train_time = train_model(X_train_scaled, y_train_encoded, model)
    y_pred, predict_time = evaluate_model(X_test_scaled, model)

    y_train_decoded = decode_y(y_train_encoded, le)
    y_test_decoded = decode_y(y_test_encoded, le)

    results = save_map_of_model_metrics(y_test_encoded, y_pred, train_time, predict_time, name, results)

print(results)