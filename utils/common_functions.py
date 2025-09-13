import os
import pandas
from src.logger import logging
from src.exception.exception import CustomException
import yaml


def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path")
        
        with open(file_path,"r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logging.info("Succesfully read the YAML file")
            return config
    
    except Exception as e:
        logging.error("Error while reading YAML file")
        raise CustomException("Failed to read YAMl file" , e)