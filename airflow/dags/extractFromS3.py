from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils import timezone
from datetime import timedelta

import boto3
from airflow.hooks.base import BaseHook

import os
import sys
import pandas as pd
import io
from dotenv import load_dotenv

load_dotenv()

default_args = {
    'owner': 'airflow',
    'start_date': timezone.utcnow() - timedelta(days=1)
}

bucket_name = 'metrai-documents-dev'
s3_prefix = 'anime/'
target_file = 'animelist.csv'
max_rows = 5000000   

with DAG(
    dag_id='ETL_pipeline_S3',
    description='extract csv data from S3, preprocess it and then load to postgres',
    default_args=default_args,
    schedule='@daily',
    catchup=False
) as dag:
    
    # Wait until the file exists in S3
    wait_for_file = S3KeySensor(
        task_id="wait_for_file",
        bucket_key=f"{s3_prefix}{target_file}",  # 👈 no s3:// prefix
        bucket_name=bucket_name,
        aws_conn_id="aws_default",
        poke_interval=30,
        timeout=60 * 30,
        mode='reschedule'
    )

    @task
    def extract_from_s3():
        """List files in S3 and return the key of target CSV."""
        try:
            conn = BaseHook.get_connection("aws_default")
            s3 = boto3.client(
                "s3",
                aws_access_key_id=conn.login,
                aws_secret_access_key=conn.password,
                region_name=conn.extra_dejson.get("region_name")
            )

            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)

            print(f"Found {len(response.get('Contents', []))} objects in S3")

            for s3_obj in response.get('Contents', []):
                key = s3_obj['Key']

                if key.endswith('/'):
                    continue

                filename = os.path.basename(key)
                if filename == target_file:
                    return key  
                
        except Exception as e:
            raise Exception

    @task
    def process_data(key: str):
        """Read CSV from S3 and process it into a DataFrame."""
        try:
            conn = BaseHook.get_connection("aws_default")
            s3 = boto3.client(
                "s3",
                aws_access_key_id=conn.login,
                aws_secret_access_key=conn.password,
                region_name=conn.extra_dejson.get("region_name")
            )

            file = s3.get_object(Bucket=bucket_name, Key=key)

            # Use NamedTemporaryFile to store CSV temporarily
            import tempfile

            with tempfile.NamedTemporaryFile(mode='wb', suffix=".csv", delete=False) as tmp_file:
                for chunk in iter(lambda: file["Body"].read(1024 * 1024), b""):  # 1 MB chunks
                    tmp_file.write(chunk)

                tmp_file.flush()

                print(f"Downloaded S3 file to {tmp_file.name}")

                return tmp_file.name

        except Exception as e:
            raise Exception

    @task
    def upload_to_postgres(temp_file: str):
        """Upload processed DataFrame to Postgres."""
        try:

            pg_hook = PostgresHook(postgres_conn_id="postgres_default")
            engine = pg_hook.get_sqlalchemy_engine()

            
            i = 0
            chunksize = 100000
            for chunk in pd.read_csv(temp_file, nrows=max_rows,chunksize=chunksize):
                if_exists = 'replace' if i == 0 else 'append'
                chunk.to_sql("animelist", engine, if_exists=if_exists, index=False, chunksize=10000)

                i += 1

                print(f"uploaded {len(chunk)} rows to postgres")
        except Exception as e:
            raise Exception
    
    # Define task dependencies (using XComs under the hood)
    key = extract_from_s3()
    data = process_data(key)
    upload_to_postgres(data)

    wait_for_file >> key
