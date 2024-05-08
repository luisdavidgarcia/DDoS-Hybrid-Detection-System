import tensorflow as tf
from tensorflow.keras.layers import Conv1D, Conv1DTranspose, Dense, Flatten, Reshape
from tensorflow.keras.models import Model, Sequential

class Conv1DAutoencoder(Model):
    def __init__(self):
        super(Conv1DAutoencoder, self).__init__()
        self.encoder = self._build_encoder()
        self.decoder = self._build_decoder()

    def _build_encoder(self):
        encoder = Sequential([
            Conv1D(32, 3, strides=2, padding='same', activation='relu'),
            Conv1D(16, 3, strides=2, padding='same', activation='relu'),
            # Conv1D(8, 3, strides=2, padding='same', activation='relu')
        ], name='encoder')

        return encoder
    
    def _build_decoder(self):
        decoder = Sequential([
            # Conv1DTranspose(8, 3, strides=1, padding='same', activation='relu'),
            Conv1DTranspose(16, 3, strides=2, padding='same', activation='relu'),
            Conv1DTranspose(32, 3, strides=2, padding='same', activation='relu'),
            Conv1DTranspose(1, 3, strides=1, padding='same', activation='sigmoid')
        ], name='decoder')

        return decoder

    def call(self, inputs):
        encoded = self.encoder(inputs)
        decoded = self.decoder(encoded)
        return decoded