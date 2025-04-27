import os
import pandas as pd
from minio import Minio
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from utils.common_function import read_yaml, read_json_credentials

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config, credentials):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_name"]  # Expecting a list of filenames

        self.access_key = credentials["access_key"]
        self.secret_key = credentials["secret_key"]

        # Ensure RAW_DIR exists
        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data Ingestion initialized with bucket: {self.bucket_name}, files: {self.file_names}")

    def download_csvs_from_minio(self):
        try:
            client = Minio(
                "localhost:9000",
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=False
            )

            downloaded_paths = []

            for file_name in self.file_names:
                local_path = os.path.join(RAW_DIR, file_name)

                client.fget_object(
                    bucket_name=self.bucket_name,
                    object_name=file_name,
                    file_path=local_path
                )

                logger.info(f"Downloaded '{file_name}' successfully to {local_path}")
                downloaded_paths.append(local_path)

            return downloaded_paths

        except Exception as e:
            logger.error("Error while downloading CSV files from Minio")
            raise CustomException("Failed to download CSV files", e)

    def run(self):
        try:
            logger.info("Starting data ingestion process")

            file_paths = self.download_csvs_from_minio()

            logger.info("Data ingestion completed successfully")

        except CustomException as ce:
            logger.error(str(ce))

        finally:
            logger.info("Data ingestion Completed")

if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    credentials = read_json_credentials(CREDENTIALS_PATH)

    data_ingestion = DataIngestion(config=config, credentials=credentials)
    data_ingestion.run()
