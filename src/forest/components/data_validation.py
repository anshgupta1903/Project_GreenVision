import sys
import pandas as pd
from pandas import DataFrame
from src.forest.exception import ForestException
from src.forest.logger import logging
from src.forest.utils.main_utils import read_yaml_file
from src.forest.constant.training_pipeline import SCHEMA_FILE_PATH
from src.forest.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from src.forest.entity.config_entity import DataValidationConfig


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_validation_config = data_validation_config
        self.schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
    
    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:
        try: 
            status = len(dataframe.columns) == len(self._schema_config['columns'])
            logging.info(f"Is required column present: {status}")
            return status
        except Exception as e: 
            raise ForestException(e, sys)
    @staticmethod
    def read_data(file_path) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ForestException(e, sys)
    

    def is_numerical_column_exist(self, dataframe: DataFrame) -> bool:
        try:
            numerical_columns = self.schema_config['numerical_columns']
            dataframe_columns = dataframe.columns
            status = True
            missing_numerical_columns = []
            for columns in numerical_columns:
                if columns not in dataframe_columns:
                    status = False
                    missing_numerical_columns.append(columns)
            logging.info(f"Missing numerical columns:{missing_numerical_columns}")
            return status
        except Exception as e:
            raise ForestException(e, sys) from e
    

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logging.info("Starting data validation")
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            logging.info("Validating number of columns in training data")
            train_status = self.validate_number_of_columns(train_dataframe)
            logging.info("Validating number of columns in testing data")
            test_status = self.validate_number_of_columns(test_dataframe)

            logging.info("Checking numerical columns in training data")
            train_numerical_status = self.is_numerical_column_exist(train_dataframe)
            logging.info("Checking numerical columns in testing data")
            test_numerical_status = self.is_numerical_column_exist(test_dataframe)

            data_validation_artifact = DataValidationArtifact(
                schema_file_path=SCHEMA_FILE_PATH,
                report_file_path=self.data_validation_config.report_file_path,
                trained_file_path=train_file_path,
                test_file_path=test_file_path,
                is_train_validated=train_status,
                is_test_validated=test_status,
                is_train_numerical_column_exist=train_numerical_status,
                is_test_numerical_column_exist=test_numerical_status
            )

            logging.info(f"Data Validation Artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise ForestException(e, sys) from e

        
        
    