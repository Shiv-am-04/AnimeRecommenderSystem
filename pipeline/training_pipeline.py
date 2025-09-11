from src.recommendation_workflow.data_preprocessing import DataProcessor
from src.recommendation_workflow.model_training import ModelTraining
from config.paths_config import *

if __name__ == "__main__":
    processor = DataProcessor(ANIMELIST_CSV,PROCESSED_DIR)
    processor.run()

    trainer = ModelTraining(PROCESSED_DIR)
    trainer.train_model()