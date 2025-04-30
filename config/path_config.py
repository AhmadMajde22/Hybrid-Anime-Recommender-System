import os

# Directories for Data Ingestion (only RAW_DIR is needed)
RAW_DIR = "artifacts/raw"

# Ensure the RAW directory exists
os.makedirs(RAW_DIR, exist_ok=True)

# Paths for configuration and credentials
CONFIG_PATH = "config/config.yaml"
CREDENTIALS_PATH = "config/credentials.json"


### Data Processing

PROCESSED_DIR = r"artifacts/processed"
ANIMELIST_CSV = r"artifacts/raw/animelist.csv"
ANIME_CSV = r"artifacts/raw/anime.csv"
ANIME_SYNOPSIS_CSV =r"artifacts/raw/anime_with_synopsis.csv"


X_TRAIN_ARRAY = os.path.join(PROCESSED_DIR,"X_train.array.pkl")
X_TEST_ARRAY = os.path.join(PROCESSED_DIR,"X_test.array.pkl")
Y_TRAIN = os.path.join(PROCESSED_DIR,"y_train.array.pkl")
Y_TEST = os.path.join(PROCESSED_DIR,"y_test.array.pkl")

RATING_DF = os.path.join(PROCESSED_DIR,"rating_df.csv")
DF = os.path.join(PROCESSED_DIR,"anime_df.csv")
SYNOPSIS_DF =os.path.join(PROCESSED_DIR,"synopsis_df.csv")

USER2USER_ENCODED =r"artifacts/processed/user2user_encoded.pkl"
USER2USER_DECODED = r"artifacts/processed/user2user_decoded.pkl"

ANIME2ANIME_ENCODED = r"artifacts/processed/anime2anime_encoded.pkl"
ANIME2ANIME_DECODED =r"artifacts/processed/anime2anime_decoded.pkl"
