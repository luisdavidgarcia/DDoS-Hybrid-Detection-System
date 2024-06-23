import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard
import datetime

def create_tensorboard_callback():
    """Creates a TensorBoard callback ready to use for model training."""
    log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)
    return tensorboard_callback

# Example of adding more callbacks
def create_early_stopping_callback():
    """Creates an early stopping callback to avoid overfitting."""
    return tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, verbose=1)
