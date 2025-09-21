import os
from src.logger import logging
from src.exception.exception import CustomException

from dotenv import load_dotenv

load_dotenv()


def read_yaml(file_path):
    try:
        import yaml

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path")
        
        with open(file_path,"r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logging.info("Succesfully read the YAML file")
            return config
    
    except Exception as e:
        logging.error("Error while reading YAML file")
        raise CustomException("Failed to read YAMl file" , e)
    
def establish_connection():
    from sqlalchemy import create_engine

    username = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = 'localhost'      
    port = 5433            
    database = os.getenv('DATABASE')

    # Create connection engine
    engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

    return engine
