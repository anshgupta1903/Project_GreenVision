import sys, os
import shutil
import pandas as pd
from pandas import DataFrame
from zipfile import ZipFile
from sklearn.model_selection import train_test_split    
from src.forest.entity.config_entity import DataIngestionConfig
from src.forest.entity.artifact_entity import DataIngestionArtifact

from src.forest.exception import ForestException
from src.forest.logger import logging
from src.forest.utils.main_utils import read_yaml_file, create_directories
from src.forest.constant.training_pipeline import SCHEMA_FILE_PATH
from src.forest.data_access.forest_data import ForestData


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig=DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise ForestException(e, sys)
        
    def export_data_into_feature_store(self) -> DataFrame:

        try:
            logging.info("Exporting  data from MongoDb to feature store")
            sensor_data: DataFrame = ForestData()
            dataframe = sensor_data.export_collection_as_dataframe(collection_name=self.data_ingestion_config.collection_name)
            logging.info(f"Shape of dataframe: {dataframe.shape}")
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.mkdirs(dir_path, exist_ok = True)
            logging.info(f"Saving exported data into feature store file path: {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        
        except Exception as e:
            raise ForestException(e, sys)

    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        try:
            logging.info("Splitting data into train and test")
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.test_size, random_state=42)
            logging.info("Completed splitting data into train and test")
            dir_path = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Saving training data to file path: {self.data_ingestion_config.train_file_path}")
            train_set.to_csv(self.data_ingestion_config.train_file_path, index=False, header=True)
            logging.info(f"Saving testing data to file path: {self.data_ingestion_config.test_file_path}")
            test_set.to_csv(self.data_ingestion_config.test_file_path, index=False, header=True)
        except Exception as e:
            raise ForestException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info("Starting data ingestion")
            dataframe = self.export_data_into_feature_store()
            self.split_data_as_train_test(dataframe=dataframe)
            data_ingestion_artifact = DataIngestionArtifact(
                feature_store_file_path=self.data_ingestion_config.feature_store_file_path,
                train_file_path=self.data_ingestion_config.train_file_path,
                test_file_path=self.data_ingestion_config.test_file_path
            )
            logging.info(f"Data Ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise ForestException(e, sys)

            

