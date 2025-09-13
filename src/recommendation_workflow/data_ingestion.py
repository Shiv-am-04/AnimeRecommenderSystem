import os
import pandas as pd
from google.cloud import storage
from src.logger import logging
from src.exception.exception import CustomException
from config.paths_config import *

from utils.common_functions import read_yaml

from dotenv import load_dotenv
import os
import sys

load_dotenv()

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_names = self.config["bucket_file_names"]

        os.makedirs(RAW_DIR,exist_ok=True)

        logging.info("Data Ingestion Started....")
    
    def upload_to_s3(self):
        import boto3

        # Create an S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        # Local file path and S3 bucket details
        local_folder = r'artifacts\raw'
        bucket_name = 'metrai-documents-dev'
        s3_prefix = 'anime/'  # The path inside the bucket

        for root,dirs,files in os.walk(local_folder):
            for file in files:
                local_file = os.path.join(root,file)
                relative_path = os.path.relpath(local_file,local_folder)
                s3_key = os.path.join(s3_prefix,relative_path).replace("\\", "/")

                # upload file
                try:
                    s3.upload_file(local_file,bucket_name,s3_key)
                    logging.info(f"Uploaded {file} to the {bucket_name}")
                except Exception as e:
                    CustomException(e,sys)

    def download_csv_from_s3(self):
        try:
            import boto3

            s3 = boto3.client(
                's3'
            )

            local_folder = r'artifacts\raw'
            bucket_name = 'metrai-documents-dev'
            s3_prefix = 'anime/'

            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)


            for object in response.get('Contents',[]):
                key = object['Key']

                if key.endswith('/'):
                    continue

                file_name = os.path.basename(key)

                if file_name == 'animelist.csv':
                    local_path = os.path.join(local_folder,file_name)

                    s3.download_file(bucket_name,key,local_path)

                    data = pd.read_csv(local_path,nrows=5000000)
                    data.to_csv(local_path,index=False)

                    logging.info(f"{file_name} downloaded to the {local_path}")

        except Exception as e:
            raise CustomException(e,sys)
            

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
            # self.download_csv_from_gcp()
            self.download_csv_from_s3()
            logging.info("Data Ingestion Completed...")
        except CustomException as ce:
            logging.error(f"CustomException : {str(ce)}")
        finally:
            logging.info("Data Ingestion DONE...")

if __name__ == "__main__":
    ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    ingestion.run()