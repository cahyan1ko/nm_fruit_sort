from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db
