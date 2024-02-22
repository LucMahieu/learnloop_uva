from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import streamlit as st

@st.cache_resource
def init_connection(username, password, host):
    # Aangepast om SSL en andere CosmosDB-specifieke parameters te gebruiken
    uri = (f"mongodb://{username}:{password}@{host}/?ssl=true"
           "&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000"
           "&appName=@learnloop-test@")
    
    print(f"This is the URI: {uri}")
    
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)
        return None
