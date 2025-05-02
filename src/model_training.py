import os
import comet_ml
import joblib
import numpy as np
from tensorflow.keras.callbacks import (
    ModelCheckpoint, LearningRateScheduler, EarlyStopping
)

from src.logger import get_logger
from src.custom_exception import CustomException
from src.base_model import BaseModel
from config.path_config import *

logger = get_logger(__name__)


class ModelTraining:
    def __init__(self, data_path):
        self.data_path = data_path
        logger.info("Model Training initialized...")

        self.experiment = comet_ml.Experiment(
            api_key="HLbTSFvefsbXbxkzSkCf2Rm2l",
            project_name="hayprid-anime-recommendation-system",
            workspace="ahmadmajde22"
        )

    def load_data(self):
        """Loads preprocessed training and test data from joblib files."""
        try:
            X_train_array = joblib.load(X_TRAIN_ARRAY)
            X_test_array = joblib.load(X_TEST_ARRAY)
            y_train = joblib.load(Y_TRAIN)
            y_test = joblib.load(Y_TEST)

            logger.info("Data loaded successfully for model training.")
            return X_train_array, X_test_array, y_train, y_test

        except Exception as e:
            logger.error("Error occurred while loading the data.")
            raise CustomException("Failed to load data", e)

    def train_model(self):
        """Constructs, compiles, and trains the model with callbacks."""
        try:
            # Load data
            X_train_array, X_test_array, y_train, y_test = self.load_data()

            # Load encoded users and animes
            n_users = len(joblib.load(USER2USER_ENCODED))
            n_animes = len(joblib.load(ANIME2ANIME_ENCODED))

            # Initialize base model
            base_model = BaseModel(config_path=CONFIG_PATH)
            model = base_model.RecommenderNet(n_users=n_users, n_animes=n_animes)

            # Learning rate scheduling config
            start_lr = 1e-5
            min_lr = 1e-5
            max_lr = 5e-5
            rampup_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            batch_size = base_model.config["model"]["batch_size"]  # type: ignore
            epochs = base_model.config["model"]["epochs"]  # type: ignore

            def lrfn(epoch):
                if epoch < rampup_epochs:
                    return (max_lr - start_lr) / rampup_epochs * epoch + start_lr
                elif epoch < rampup_epochs + sustain_epochs:
                    return max_lr
                else:
                    return (max_lr - min_lr) * exp_decay**(epoch - rampup_epochs - sustain_epochs) + min_lr

            # Setup callbacks and create required directories
            lr_callback = LearningRateScheduler(lrfn, verbose=0)

            model_checkpoint = ModelCheckpoint(
                filepath=CHECKPOINT_FILE_PATH,
                save_weights_only=True,
                monitor='val_loss',
                mode='min',
                save_best_only=True
            )

            early_stopping = EarlyStopping(
                patience=3,
                monitor='val_loss',
                mode='min',
                restore_best_weights=True
            )

            callbacks = [model_checkpoint, lr_callback, early_stopping]

            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH), exist_ok=True)
            os.makedirs(MODEL_DIR, exist_ok=True)
            os.makedirs(WEIGHTS_DIR, exist_ok=True)

            logger.info("Callbacks and directories set up successfully.")

            # Train the model
            history = model.fit(
                x=X_train_array,
                y=y_train,
                batch_size=batch_size,
                epochs=epochs,
                verbose=1,
                validation_data=(X_test_array, y_test),
                callbacks=callbacks
            )

            logger.info("Model training completed.")

            # Load best weights from checkpoint
            model.load_weights(CHECKPOINT_FILE_PATH)
            logger.info("Best model weights loaded from checkpoint.")

            # Log metrics to CometML
            try:
                for epoch in range(len(history.history['loss'])):
                    self.experiment.log_metric('train_loss', history.history['loss'][epoch], step=epoch)
                    self.experiment.log_metric('val_loss', history.history['val_loss'][epoch], step=epoch)

                logger.info("Logged experiment metrics successfully.")
            except Exception as e:
                logger.error(f"Error logging metrics to CometML: {e}")

            return model  # Return trained model

        except Exception as e:
            logger.error("Error occurred during the model training pipeline.")
            raise CustomException("Failed to train the model", e)

    def extract_weights(self, layer_name: str, model):
        """
        Extract and normalize weights from a specified layer in the model.
        """
        try:
            weight_layer = model.get_layer(layer_name)
            weights = weight_layer.get_weights()[0]

            # Normalize weights
            norm_weights = weights / np.linalg.norm(weights, axis=1, keepdims=True)

            logger.info(f"Weights extracted and normalized from layer: {layer_name}")
            return norm_weights

        except Exception as e:
            logger.error(f"Failed to extract weights from layer: {layer_name}")
            raise CustomException(f"Error extracting weights from layer '{layer_name}'", e)

    def save_model_weights(self, model):
        """
        Save the full trained model to disk.
        """
        try:
            model.save(MODEL_PATH)
            logger.info(f"Model saved successfully to {MODEL_PATH}")

            user_weights = self.extract_weights("user_embedding", model)
            anime_weights = self.extract_weights("anime_embedding", model)

            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(anime_weights, ANIME_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)



            logger.info("User and anime weights saved successfully.")

        except Exception as e:
            logger.error("Failed to save the model.")
            raise CustomException("Error saving the model to disk", e)


if __name__ == "__main__":
    model_trainer = ModelTraining(PROCESSED_DIR)
    model = model_trainer.train_model()  # ← Capture returned model
    model_trainer.save_model_weights(model=model)  # ← Pass it here
