from models.cnn_autoencoder import Conv1DAutoencoder
from utils.only_benign_data_sampling import prepare_norm_balanced_data
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from sklearn.metrics import f1_score
import pandas as pd

# Load and prepare data with labels for the validation set (to include both benign and attack logs)
print('Loading and preparing data...')
df = pd.read_csv('datasets/cic_ids_2018/cleaned_combined.csv')
# Use all data instead of only benign to include labels in validation set
x_train_scaled, x_test_scaled = prepare_norm_balanced_data(df)

# Print dimensions of preprocessed data
print("Dimensions of preprocessed data:")
print("x_train_scaled shape:", x_train_scaled.shape)
print("x_test_scaled shape:", x_test_scaled.shape)

input_dim = x_train_scaled.shape[1]

# Initialize and compile the model
model = Conv1DAutoencoder()
opt = Adam(learning_rate=1e-4)
model.compile(
    optimizer=opt, 
    loss='mse',
    metrics=['AUC']
)
model.build(input_shape=(None, input_dim, 1))
model.encoder.summary()
model.decoder.summary()
model.summary()

# Configure ModelCheckpoint to save the model with the best validation AUC score
# checkpoint = ModelCheckpoint('best_model.h5', monitor='val_auc', mode='max', save_best_only=True, verbose=1)
log_folder = 'logs/'
tensorboard_callback = TensorBoard(
    log_dir=log_folder,
    histogram_freq=1,
    write_graph=True,
    write_images=True,
    update_freq='epoch',
    profile_batch=2,
    embeddings_freq=1
)

lr_scheduler = ReduceLROnPlateau(
    monitor='val_loss', 
    factor=0.5, 
    patience=3, 
    min_lr=1e-7, 
    verbose=1
)

# Train the model while evaluating validation AUC scores
model.fit(
    x_train_scaled, x_train_scaled,
    epochs=40,
    batch_size=64,
    validation_data=(x_test_scaled, x_test_scaled),
    callbacks=[tensorboard_callback],
)

# Predict
history = model.predict(x_test_scaled)

model_f1 = f1_score(x_test_scaled, history, average='samples')
print(f'F1 Score: {model_f1}')