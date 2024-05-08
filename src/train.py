from models.cnn_autoencoder import Conv1DAutoencoder
from utils.data_preprocessing import prepare_norm_balanced_data

import pandas as pd

# Load and prepare the data
print('Loading and preparing data...')
df = pd.read_csv('datasets/cic_ids_2018/02-15-2018.csv')
print("Preview of the data:")
print(df.head())

x_train_scaled, x_test_scaled, y_train, y_test, label_mapping = prepare_norm_balanced_data(df)

# Print dimensions of preprocessed data
print("Dimensions of preprocessed data:")
print("x_train_scaled shape:", x_train_scaled.shape)
print("x_test_scaled shape:", x_test_scaled.shape)

# Test building model and output the summary
model = Conv1DAutoencoder()
model.compile(optimizer='adam', loss='mse')
model.build(input_shape=(None, 68, 1))
model.encoder.summary()
model.decoder.summary()
model.summary()

# Train the model using the preprocessed data
model.fit(x_train_scaled, x_train_scaled, epochs=10, batch_size=32, validation_data=(x_test_scaled, x_test_scaled))
