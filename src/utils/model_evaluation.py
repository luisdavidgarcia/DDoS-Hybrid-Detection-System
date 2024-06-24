# src/utils/model_evaluation.py

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

import matplotlib.pyplot as plt
import seaborn as sns
import time

def decode_y(y, label_encoder):
    return label_encoder.inverse_transform(y)

def train_model(X_train, y_train, model):
    start_train_time = time.time()
    model.fit(X_train, y_train)
    end_train_time = time.time()
    train_time = end_train_time - start_train_time

    return model, train_time

def evaluate_model(X_test, model):
    start_predict_time = time.time()
    y_pred = model.predict(X_test)
    end_predict_time = time.time()
    predict_time = end_predict_time - start_predict_time

    return y_pred, predict_time

def save_map_of_model_metrics(y_test, y_pred, train_time, predict_time, model_name, metrics_dict, average='weighted'):
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average=average),
        'recall': recall_score(y_test, y_pred, average=average),
        'f1': f1_score(y_test, y_pred, average=average),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'class_report': classification_report(y_test, y_pred),
        'train_time': train_time,
        'predict_time': predict_time
    }
    metrics_dict[model_name] = metrics
    return metrics_dict

def plot_confusion_matrix(y_true, y_pred, label_encoder):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()
