from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
import string
import random

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')

# Init db
# COSMOS_URI = os.getenv('COSMOS_URI')
# db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
MONGO_URI = os.getenv('MONGO_DB')
db_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = db_client.LearnLoop

# Make authentication instance for the flask app
auth = OAuth(app)

auth.register(
    name='surfconext',
    client_id=os.getenv('SURFCONEXT_CLIENT_ID'),
    client_secret=os.getenv('SURFCONEXT_CLIENT_SECRET'),
    server_metadata_url=os.getenv('SURFCONEXT_METADATA_URL'),
    client_kwargs={'scope': 'openid'}
)


@app.route('/')
def login():
    redirect_uri = url_for('authorize', _external=True)
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

    # nonce='test_nonce'

    # Redirect to streamlit app
    redirect_url = f'http://localhost:8501/app?nonce={nonce}'
    return redirect(redirect_url, code=302)


if __name__=="__main__":
    app.run(host='0.0.0.0', port=3000)