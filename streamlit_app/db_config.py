from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

running_on_premise = False # Set to true if IP adres is allowed by Gerrit

load_dotenv()


def connect_db():
    # Database connection
    if running_on_premise:
        COSMOS_URI = os.getenv('COSMOS_URI')
        db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
    else:
        MONGO_URI = os.getenv('MONGO_DB')
        db_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

    db = db_client.LearnLoop

    # Ping database to check if it's connected
    try:
        db.command("ping")
        # print("Connected to database")
    except Exception as e:
        print(f"Error: {e}")
    
    return db