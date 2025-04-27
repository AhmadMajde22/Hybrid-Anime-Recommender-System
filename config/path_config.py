import os

# Directories for Data Ingestion (only RAW_DIR is needed)
RAW_DIR = "artifacts/raw"

# Ensure the RAW directory exists
os.makedirs(RAW_DIR, exist_ok=True)

# Paths for configuration and credentials
CONFIG_PATH = "config/config.yaml"
CREDENTIALS_PATH = "config/credentials.json"
