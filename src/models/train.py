from cnn_autoencoder import Conv1DAutoencoder

# Test building model and output the summary
model = Conv1DAutoencoder()
model.compile(optimizer='adam', loss='mse')
model.build(input_shape=(None, 128, 1))
model.summary()