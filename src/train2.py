import numpy as np
import pandas as pd
import time
import json
import psutil
import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score
from xgboost import XGBClassifier

from utils.all_samples_data_preprocessing import prepare_norm_balanced_data

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, UpSampling1D, Dense, Flatten, Reshape
from tensorflow.keras.callbacks import TensorBoard

# Load your dataset
df = pd.read_csv('datasets/cic_ids_2018/cleaned_combined.csv')

# Split data for autoencoder and classifier
x_train, x_test, y_train, y_test, label_map = prepare_norm_balanced_data(df)

input_dim = x_train.shape[1]

# Reshape data for Conv1D
x_train_reshaped = x_train.values.reshape((x_train.shape[0], x_train.shape[1], 1))
x_test_reshaped = x_test.values.reshape((x_test.shape[0], x_test.shape[1], 1))

input_layer = Input(shape=(input_dim, 1))
x = Conv1D(32, 3, activation='relu', padding='same')(input_layer)
x = MaxPooling1D(2, padding='same')(x)
x = Conv1D(16, 3, activation='relu', padding='same')(x)
x = MaxPooling1D(2, padding='same')(x)
x = Flatten()(x)
bottleneck = Dense(16, activation='relu')(x)

x = Dense((input_dim // 4) * 16, activation='relu')(bottleneck)
x = Reshape(((input_dim // 4), 16))(x)
x = UpSampling1D(2)(x)
x = Conv1D(16, 3, activation='relu', padding='same')(x)
x = UpSampling1D(2)(x)
output_layer = Conv1D(1, 3, activation='sigmoid', padding='same')(x)

autoencoder = Model(input_layer, output_layer)
encoder = Model(input_layer, bottleneck)
autoencoder.compile(optimizer='adam', loss='mse')

# Set up TensorBoard
log_dir = 'logs'
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1, write_graph=True, write_images=True)

class CustomCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        training_time = time.time() - self.start_time
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        logs['training_time'] = training_time
        logs['cpu_usage'] = cpu_usage
        logs['memory_usage'] = memory_info.percent
        with open('metrics.json', 'a') as f:
            json.dump(logs, f)
            f.write('\n')

    def on_epoch_begin(self, epoch, logs=None):
        self.start_time = time.time()

class AUCCallback(tf.keras.callbacks.Callback):
    def __init__(self, validation_data, log_dir):
        super().__init__()
        self.validation_data = validation_data
        self.log_dir = log_dir

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        x_val, y_val = self.validation_data
        y_pred = self.model.predict(x_val)
        auc = roc_auc_score(y_val, y_pred)
        logs['val_auc'] = auc
        with tf.summary.create_file_writer(self.log_dir).as_default():
            tf.summary.scalar('val_auc', auc, step=epoch)
        print(f"Epoch {epoch+1}: val_auc = {auc:.4f}")

autoencoder_start_time = time.time()
# Train the autoencoder on both benign and attack samples
autoencoder.fit(x_train_reshaped, x_train_reshaped, epochs=50, batch_size=256, shuffle=True, validation_split=0.2, callbacks=[tensorboard_callback, CustomCallback(), AUCCallback((x_test_reshaped, y_test), log_dir)])
autoencoder_end_time = time.time()
autoencoder_training_time = autoencoder_end_time - autoencoder_start_time

# Encode the train and test data using the trained encoder
encoded_train = encoder.predict(x_train_reshaped)
encoded_test = encoder.predict(x_test_reshaped)

# Flatten the encoded data for combining
encoded_train_flat = encoded_train.reshape((encoded_train.shape[0], -1))
encoded_test_flat = encoded_test.reshape((encoded_test.shape[0], -1))

# Combine original and encoded features
combined_train = np.concatenate((x_train.values, encoded_train_flat), axis=1)
combined_test = np.concatenate((x_test.values, encoded_test_flat), axis=1)

# Train the XGBoost classifier
xgb_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)

start_train_time = time.time()
xgb_model.fit(combined_train, y_train)
end_train_time = time.time()

train_time = end_train_time - start_train_time

# Evaluate the model
start_predict_time = time.time()
y_pred = xgb_model.predict(combined_test)
end_predict_time = time.time()

predict_time = end_predict_time - start_predict_time

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Print the results
print(f"Model Accuracy: {accuracy:.2f}")
print(f"Model Precision: {precision:.2f}")
print(f"Model Recall: {recall:.2f}")
print(f"Model F1 Score: {f1:.2f}")
print(f"XGBoost Training Time: {train_time:.2f} seconds")
print(f"XGBoost Prediction Time: {predict_time:.2f} seconds")
print(f"Autoencoder Training Time: {autoencoder_training_time:.2f} seconds")

# Save the results to a file
metrics = {
    'accuracy': accuracy,
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'training_time': train_time,
    'prediction_time': predict_time,
    'autoencoder_training_time': autoencoder_training_time,
    'cpu_usage': psutil.cpu_percent(),
    'memory_usage': psutil.virtual_memory().percent,
}

with open('metrics.json', 'a') as f:
    json.dump(metrics, f)
    f.write('\n')

# Generate confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Map the encoded labels to their actual names
labels = [label_map[label] for label in np.unique(y_test)]

# Plot confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=labels)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()
