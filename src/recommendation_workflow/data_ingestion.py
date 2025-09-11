import os
import pandas as pd
from google.cloud import storage
from src.logger import logging
from src.exception import CustomException
from config.paths_config import *


class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_names"]

        os.makedirs(RAW_DIR,exist_ok=True)

        logging.info("Data Ingestion Started....")

    def download_csv_from_gcp(self):
        try:

            client  = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR,file_name)

                if file_name=="animelist.csv":
                    # In Google Cloud Storage, a blob is essentially a file or object stored inside a bucket. It could be:
                    # - A CSV file
                    # - An image
                    # - A model checkpoint
                    # - Any binary or text data

                    # We're creating a reference to a file named file_name inside the bucket — whether it exists yet or not
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path,nrows=5000000)
                    data.to_csv(file_path,index=False)
                    logging.info("Large file detected Only downloading 5M rows")
                else:
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    logging.info("Downloading Smaller Files ie anime and anime_with synopsis")
        
        except Exception as e:
            logging.error("Error while downloading data from GCP")
            raise CustomException("Failed to download data",e)
        
    def run(self):
        try:
            logging.info("Starting Data Ingestion Process....")
            self.download_csv_from_gcp()
            logging.info("Data Ingestion Completed...")
        except CustomException as ce:
            logging.error(f"CustomException : {str(ce)}")
        finally:
            logging.info("Data Ingestion DONE...")

if __name__ == "__main__":
    ingestion = DataIngestion()