import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from utils.all_samples_data_preprocessing import prepare_norm_balanced_data
from xgboost import XGBClassifier
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, UpSampling1D, Dense, Flatten, Reshape
from tensorflow.keras.optimizers import Adam

# Load your dataset
df = pd.read_csv('datasets/cic_ids_2018/02-15-2018.csv')

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

# Train the autoencoder on both benign and attack samples
autoencoder.fit(x_train_reshaped, x_train_reshaped, epochs=50, batch_size=256, shuffle=True, validation_split=0.2)

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
xgb_model.fit(combined_train, y_train)

# Evaluate the model
accuracy = xgb_model.score(combined_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")
