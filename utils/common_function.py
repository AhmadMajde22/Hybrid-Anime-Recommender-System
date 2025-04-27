import os
import yaml
import json
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found at {file_path}")

        with open(file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info(f"Successfully read the YAML file from {file_path}")
            return config

    except Exception as e:
        logger.error(f"Error while reading YAML file: {e}")
        raise CustomException("Failed to read YAML file", e)


def read_json_credentials(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Credentials file not found at {file_path}")

        with open(file_path, 'r') as file:
            credentials = json.load(file)

            # Normalize key names
            access_key = credentials.get("access_key") or credentials.get("accessKey")
            secret_key = credentials.get("secret_key") or credentials.get("secretKey")

            if not access_key or not secret_key:
                raise ValueError("Missing 'access_key' or 'secret_key' in credentials file.")

            logger.info(f"Successfully read credentials from {file_path}")
            return {
                "access_key": access_key,
                "secret_key": secret_key
            }

    except Exception as e:
        logger.error(f"Error while reading JSON credentials file: {e}")
        raise CustomException("Failed to read JSON credentials file", e)


def load_data(path):
    try:
        logger.info(f"Loading data from {path}")

        if isinstance(path, str):
            return pd.read_csv(path)
        elif isinstance(path, list):
            # If multiple paths are given, load each and return a list of DataFrames
            return [pd.read_csv(p) for p in path]
        else:
            raise ValueError("Path must be a string or a list of strings.")

    except Exception as e:
        logger.error(f"Error loading data from {path}: {e}")
        raise CustomException("Failed to load data", e)
