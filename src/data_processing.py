import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *

logger = get_logger(__name__)


class DataProcessor:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None
        self.x_train_array = None
        self.x_test_array = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.user2user_decoded = {}
        self.anime2anime_encoded = {}
        self.anime2anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("DataProcessor initialized.")

    # ---------------------------------------------------
    # 1. Load & Clean Data
    # ---------------------------------------------------
    def load_data(self, usecols):
        """Load ratings CSV with specified columns"""
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)
            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise CustomException("Failed to load data", sys)

    def filter_users(self, min_rating=400):
        """Filter users with at least `min_rating` interactions"""
        try:
            user_counts = self.rating_df["user_id"].value_counts() # type: ignore
            self.rating_df = self.rating_df[self.rating_df["user_id"].isin(user_counts[user_counts >= min_rating].index)].copy() # type: ignore
            logger.info("Filtered users with at least %d ratings.", min_rating)
        except Exception as e:
            logger.error(f"Failed to filter users: {e}")
            raise CustomException("Failed to filter users", sys)

    def drop_duplicates(self):
        """Drop duplicate rows in ratings"""
        try:
            before = len(self.rating_df)
            self.rating_df = self.rating_df.drop_duplicates()
            after = len(self.rating_df)
            logger.info(f"Dropped duplicates: {before - after} removed.")
        except Exception as e:
            logger.error(f"Failed to drop duplicates: {e}")
            raise CustomException("Failed to drop duplicates", sys)

    # ---------------------------------------------------
    # 2. Preprocessing
    # ---------------------------------------------------
    def scale_ratings(self):
        """Normalize ratings between 0 and 1"""
        try:
            min_rating = self.rating_df["rating"].min() # type: ignore
            max_rating = self.rating_df["rating"].max() # type: ignore

            self.rating_df["rating"] = self.rating_df["rating"].apply( # type: ignore
                lambda x: (x - min_rating) / (max_rating - min_rating)
            )

            logger.info(f"Ratings scaled from ({min_rating}, {max_rating}) to (0, 1).")
        except Exception as e:
            logger.error(f"Failed to scale ratings: {e}")
            raise CustomException("Failed to scale ratings", sys)

    def encode_data(self):
        """Map user and anime IDs to continuous integer encodings"""
        try:
            user_ids = self.rating_df["user_id"].unique().tolist() # type: ignore
            self.user2user_encoded = {x: i for i, x in enumerate(user_ids)}
            self.user2user_decoded = {i: x for i, x in enumerate(user_ids)}
            self.rating_df["user"] = self.rating_df["user_id"].map(self.user2user_encoded) # type: ignore
            logger.info("Encoded user IDs.")
        except Exception as e:
            logger.error(f"Failed to encode user IDs: {e}")
            raise CustomException("Failed encoding user IDs", sys)

        try:
            anime_ids = self.rating_df["anime_id"].unique().tolist() # type: ignore
            self.anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i: x for i, x in enumerate(anime_ids)}
            self.rating_df["anime"] = self.rating_df["anime_id"].map(self.anime2anime_encoded) # type: ignore
            logger.info("Encoded anime IDs.")
        except Exception as e:
            logger.error(f"Failed to encode anime IDs: {e}")
            raise CustomException("Failed encoding anime IDs", sys)

    # ---------------------------------------------------
    # 3. Split Data
    # ---------------------------------------------------
    def split_data(self, test_size=10000, random_state=43):
        """Shuffle and split data into train and test sets"""
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
            logger.info("Data shuffled.")
        except Exception as e:
            logger.error(f"Failed to shuffle data: {e}")
            raise CustomException("Failed to shuffle data", sys)

        try:
            X = self.rating_df[["user", "anime"]].values
            y = self.rating_df["rating"].values
            logger.info("Features and labels extracted.")
        except Exception as e:
            logger.error(f"Failed to extract features/labels: {e}")
            raise CustomException("Failed to extract features and labels", sys)

        try:
            train_size = self.rating_df.shape[0] - test_size
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            self.x_train_array = [X_train[:, 0], X_train[:, 1]]
            self.x_test_array = [X_test[:, 0], X_test[:, 1]]
            self.y_train = y_train
            self.y_test = y_test

            logger.info("Data split into train and test sets.")
        except Exception as e:
            logger.error(f"Failed to split data: {e}")
            raise CustomException("Failed to split data", sys)

    # ---------------------------------------------------
    # 4. Save Artifacts
    # ---------------------------------------------------
    def save_artifacts(self):
        """Save encoded maps and training/test data"""
        try:
            # Save encodings
            encoded_maps = {
                "user2user_encoded": self.user2user_encoded,
                "user2user_decoded": self.user2user_decoded,
                "anime2anime_encoded": self.anime2anime_encoded,
                "anime2anime_decoded": self.anime2anime_decoded
            }

            for name, data in encoded_maps.items():
                path = os.path.join(self.output_dir, f"{name}.pkl")
                joblib.dump(data, path)
                logger.info(f"Saved: {name} -> {path}")

            # Save training data
            joblib.dump(self.x_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.x_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)
            logger.info("Train/test arrays saved.")

            # Save ratings DataFrame
            self.rating_df.to_csv(RATING_DF, index=False)
            logger.info(f"Ratings DataFrame saved -> {RATING_DF}")

            logger.info("All artifacts saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save artifacts: {e}")
            raise CustomException("Failed to save artifacts", sys)

    # ---------------------------------------------------
    # 5. Process Anime Metadata
    # ---------------------------------------------------
    def process_anime_data(self):
        """Prepare anime metadata and save"""
        try:
            df = pd.read_csv(ANIME_CSV, low_memory=True)
            synopsis_df = pd.read_csv(ANIME_SYNOPSIS_CSV, low_memory=True, usecols=["MAL_ID", "Name", "Genres", "sypnopsis"])

            df.replace("Unknown", np.nan, inplace=True)
            df["anime_id"] = df["MAL_ID"]

            def get_anime_name(anime_id):
                try:
                    row = df[df['anime_id'] == anime_id]
                    eng_name = row['English name'].values[0]
                    return row['Name'].values[0] if pd.isna(eng_name) else eng_name
                except (IndexError, KeyError):
                    return f"Unknown Anime (ID: {anime_id})"

            df["eng_version"] = df["anime_id"].apply(get_anime_name)

            df.sort_values(by="Score", ascending=False, na_position="last", inplace=True)
            df = df[["anime_id", "eng_version", "Score", "Genres", "Episodes", "Type", "Members", "Premiered"]]

            df.to_csv(DF, index=False)
            synopsis_df.to_csv(SYNOPSIS_DF, index=False)

            logger.info("Anime metadata and synopsis saved successfully.")
        except Exception as e:
            logger.error(f"Failed to process anime data: {e}")
            raise CustomException("Failed to process anime data", sys)


    def run(self):
        """Executes the full data processing pipeline"""
        try:
            logger.info("Starting data processing pipeline...")

            self.load_data(usecols=['user_id', 'anime_id', 'rating'])
            self.filter_users()
            self.drop_duplicates()
            self.scale_ratings()
            self.encode_data()
            self.split_data()
            self.save_artifacts()
            self.process_anime_data()

            logger.info("Successfully completed the data processing pipeline.")

        except CustomException as e:
            logger.error(f"Pipeline failed due to a handled exception: {str(e)}")

        except Exception as e:
            logger.error(f"Pipeline failed due to an unexpected error: {str(e)}")
            raise CustomException("Unexpected error in run()", sys)

if __name__ == "__main__":
    data_processor= DataProcessor(ANIMELIST_CSV,PROCESSED_DIR)
    data_processor.run()
