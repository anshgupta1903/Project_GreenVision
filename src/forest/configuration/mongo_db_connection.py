import sys 
from src.forest.exception import ForestException
from src.forest.logger import logging
import os
from src.forest.constant.database import DATABASE_NAME
import pymongo
from pymongo import MongoClient 

import certifi
from dotenv import load_dotenv

load_dotenv()

ca = certifi.where()


class MongoDBClient:
    client = None

    def __init__(self, database_name=DATABASE_NAME) -> None:
        try:
            if MongoDBClient.client is None:
                logging.info("Creating MongoDB Client")
                mongo_db_url = os.getenv("MONGO_DB_URL")
                if mongo_db_url is None:
                    raise Exception("MONGO_DB_URL is not set in environment variables")
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.db = MongoDBClient.client[database_name]
        except Exception as e:
            raise ForestException(e, sys) from e
