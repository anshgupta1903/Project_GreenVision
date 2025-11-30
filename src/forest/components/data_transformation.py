import sys 
import numpy as np
import pandas as pd
from sklean.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from src.forest.constant import *
from src.forest.exception import ForestException
from src.forest.logger import logging
from src.forest.utils import save_object, save_numpy_array_data, read_yaml_file
from sklearn.impute import StandardScaler
from sklean.compose import ColumnTransformer
from src.forest.constant.training_pipeline import TARGET_COLUMN, SCHEMA_FILE_PATH
from src.forest.entity.config_entity import DataTransformationConfig
from src.forest.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_transformation_config: DataTransformationConfig):
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_transformation_config = data_transformation_config

    @staticmethod 
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ForestException(e, sys) from e
    def get_data_transformer_object(self) -> object:
        logging.info("Entered the get_data_transformer_object method of DataTransformation class")
        try:
            logging.info("Got numerical, categorical, transformation columns from schema config")
            _schema_config = read_yaml_file(file_path = SCHEMA_FILE_PATH)
        
            num_features = _schema_config['numerical_columns']
            categorical = _schema_config['categorical_columns']
            numerical_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy = 'median')),
                ('scaler', StandardScaler())
            ])
            logging.info(f"Numerical columns: {num_features}")
            logging.info(f"Categorical columns: {categorical}")

            preprocessor = ColumnTransformer([
                ('numerical_pipeline', numerical_pipeline, num_features)
            ])
            logging.info(f"Numerical columns: {num_features}")
            logging.info(f"Categorical columns: {categorical}")
            return preprocessor
        except Exception as e:
            raise ForestException(e, sys) from e
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
       
        logging.info("Entered the initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")
            preprocessor = self.get_data_transformer_object()
            logging.info("Obtained preprocessor object")

            train_df = DataTransformation.read_data(file_path =self.data_ingestion_artifact.train_file_path)
            test_df = DataTransformation.read_data(file_path = self.data_ingestion_artifact.test_file_path)
            
            input_feature_train_df = train_df.drop(columns = [TARGET_COLUMN], axis = 1)
            target_feature_train_df = train_df[TARGET_COLUMN]

            input_feature_test_df = test_df.drop(columns = [TARGET_COLUMN], axis = 1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            logging.info("Applying preprocessing object on training and testing dataframes")
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessor.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            logging.info("Saved transformed training and testing array")
            save_numpy_array_data(file_path = self.data_transformation_config.transformed_train_file_path, array = train_arr)
            save_numpy_array_data(file_path = self.data_transformation_config.transformed_test_file_path, array = test_arr) 
            logging.info("Saved preprocessing object")
            save_object(file_path = self.data_transformation_config.preprocessed_object_file_path, obj = preprocessor)
            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path = self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path = self.data_transformation_config.transformed_test_file_path,
                preprocessed_object_file_path = self.data_transformation_config.preprocessed_object_file_path
            )
            logging.info(f"Data Transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact 
        except Exception as e:
            raise ForestException(e, sys) from e    
    
            