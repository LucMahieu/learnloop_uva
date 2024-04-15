from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
import string
import random

load_dotenv()

# Create flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')

def connect_to_database():
    """
    Connect to either MongoDB or CosmosDB and ping to check connection.
    """
    print("Trying to connect with database")
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
        print("Connected to database")
    except Exception as e:
        print(f"Error: {e}")

    return db


@app.route('/')
def login():
    if testing:
        scheme = 'http'
    else:
        scheme = 'https'
    
    redirect_uri = url_for('authorize', _external=True, _scheme=scheme)
    return auth.surfconext.authorize_redirect(redirect_uri)


def save_id_to_db(user_id):
    user = db.users.find_one({"username": user_id})
    if not user:
        db.users.insert_one({"username": user_id})


def generate_nonce(length=16):
    """Generates a random sequence of values."""
    characters = string.ascii_letters + string.digits
    nonce = ''.join(random.choice(characters) for _ in range(length))
    return nonce


def save_nonce_to_db(user_id):
    nonce = generate_nonce(16)
    db.users.update_one({'username': user_id}, {'$set': {'nonce': nonce}})
    return nonce


@app.route('/auth')
def authorize():
    token = auth.surfconext.authorize_access_token()

    user_id = token['userinfo']['sub']
    save_id_to_db(user_id)
    nonce = save_nonce_to_db(user_id)

    # Redirect to streamlit app
    if testing:
        url = 'http://localhost:8501/'
    else:
        url = 'https://learnloop.datanose.nl/'
    
    redirect_url = f'{url}app?nonce={nonce}'

    return redirect(redirect_url, code=302)


def create_auth_instance():
    """Make authentication instance for the flask app"""
    auth = OAuth(app)

    auth.register(
        name='surfconext',
        client_id=os.getenv('SURFCONEXT_CLIENT_ID'),
        client_secret=os.getenv('SURFCONEXT_CLIENT_SECRET'),
        server_metadata_url=os.getenv('SURFCONEXT_METADATA_URL'),
        client_kwargs={'scope': 'openid'}
    )
    return auth


if __name__=="__main__":
    # Initialise settings
    running_on_premise = True # Set to true if IP adres is allowed by Gerrit
    testing = False
    
    db = connect_to_database()
    auth = create_auth_instance()
    app.run(host='0.0.0.0', port=3000)