from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
import string
import random
import db_config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')

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
    if surf_test_env:
        scheme = 'http'
    else:
        scheme = 'https'
    
    redirect_uri = url_for('authorize', _external=True, _scheme=scheme)
    return auth.surfconext.authorize_redirect(redirect_uri)


def save_id_to_db(user_id):
    user = db.users_2.find_one({"username": user_id})
    if not user:
        db.users_2.insert_one({"username": user_id})


def generate_nonce(length=16):
    """Generates a random sequence of values."""
    characters = string.ascii_letters + string.digits
    nonce = ''.join(random.choice(characters) for _ in range(length))
    return nonce


def save_nonce_to_db(user_id):
    nonce = generate_nonce(16)
    db.users_2.update_one({'username': user_id}, {'$set': {'nonce': nonce}})
    return nonce


@app.route('/auth')
def authorize():
    token = auth.surfconext.authorize_access_token()

    user_id = token['userinfo']['sub']
    save_id_to_db(user_id)
    nonce = save_nonce_to_db(user_id)

    # Redirect to streamlit app
    if surf_test_env:
        url = 'http://localhost:8501/'
    else:
        url = 'https://learnloop.datanose.nl/'
    
    redirect_url = f'{url}app?nonce={nonce}'

    return redirect(redirect_url, code=302)


if __name__=="__main__":
    # Initialise run settings: set to False for deployment
    use_mongodb = False
    surf_test_env = False

    db = db_config.connect_db(use_mongodb)
    app.run(host='0.0.0.0', port=3000)