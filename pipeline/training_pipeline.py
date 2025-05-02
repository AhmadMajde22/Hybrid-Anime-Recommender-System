from src.data_processing import DataProcessor
from src.model_training import ModelTraining
from utils.common_function import read_yaml, read_json_credentials
from config.path_config import *


def main():
    data_processor = DataProcessor(ANIMELIST_CSV, PROCESSED_DIR)
    data_processor.run()

    model_trainer = ModelTraining(PROCESSED_DIR)
    model = model_trainer.train_model()

    model_trainer.save_model_weights(model=model)


if __name__ == "__main__":
    main()
