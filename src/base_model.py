import config
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import (
    Activation, BatchNormalization, Input, Embedding, Dot,
    Dense, Flatten, Dropout
)

from utils.common_function import read_yaml
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)


class BaseModel:
    def __init__(self, config_path):
        try:
            self.config = read_yaml(config_path)
            logger.info("Loaded configuration from config.yaml")
        except Exception as e:
            raise CustomException("Error loading the configuration file", e)

    def RecommenderNet(self, n_users, n_animes):
        try:
            # Load model parameters from config
            embedding_size = self.config["model"]["embedding_size"]  # type: ignore
            dropout_rate = self.config["model"]["dropout_rate"]      # type: ignore
            loss = self.config["model"]["loss"]                      # type: ignore
            metrics = self.config["model"]["metrics"]                # type: ignore
            optimizer_cfg = self.config["model"]["optimizer"]        # type: ignore

            # Input layers
            user = Input(name='user', shape=[1])
            anime = Input(name='anime', shape=[1])

            # Embedding layers with L2 regularization
            user_embedding = Embedding(
                name='user_embedding',
                input_dim=n_users,
                output_dim=embedding_size,
                embeddings_regularizer=tf.keras.regularizers.l2(1e-6)
            )(user)

            anime_embedding = Embedding(
                name='anime_embedding',
                input_dim=n_animes,
                output_dim=embedding_size,
                embeddings_regularizer=tf.keras.regularizers.l2(1e-6)
            )(anime)

            # Interaction layer (dot product)
            x = Dot(name='dot_product', normalize=True, axes=2)([user_embedding, anime_embedding])
            x = Flatten()(x)

            # Dense block with residual connections
            def dense_block(x, units, dropout_rate=0.3):
                skip = x
                x = Dense(units, kernel_initializer='he_normal',
                          kernel_regularizer=tf.keras.regularizers.l2(1e-6))(x)
                x = BatchNormalization()(x)
                x = Activation("relu")(x)
                x = Dropout(dropout_rate)(x)
                if K.int_shape(skip)[-1] == units:
                    x = tf.keras.layers.Add()([x, skip])
                return x

            # Hidden layers with progressive reduction
            x = dense_block(x, 256, dropout_rate)
            x = dense_block(x, 128, dropout_rate)
            x = dense_block(x, 64, dropout_rate)
            x = dense_block(x, 32, dropout_rate)

            # Final dense layers
            x = Dense(16, kernel_initializer='he_normal',
                      kernel_regularizer=tf.keras.regularizers.l2(1e-6))(x)
            x = BatchNormalization()(x)
            x = Activation("relu")(x)
            x = Dropout(dropout_rate / 2)(x)

            # Output layer
            x = Dense(1, kernel_initializer='he_normal')(x)
            x = BatchNormalization()(x)
            outputs = Activation("sigmoid")(x)

            # Build and compile the model
            model = Model(inputs=[user, anime], outputs=outputs)

            # Use custom or configured optimizer
            optimizer = Adam(learning_rate=1e-3, decay=1e-4) if optimizer_cfg == "adam" else optimizer_cfg

            model.compile(
                loss=loss,
                metrics=metrics,
                optimizer=optimizer
            )

            logger.info("Model created successfully.")
            return model

        except Exception as e:
            logger.error("Error occurred during model creation.")
            raise CustomException("Failed to create the model", e)
