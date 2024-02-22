from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import certifi
import secrets

load_dotenv()

login_page = Flask(__name__)
login_page.secret_key = os.getenv('FLASK_SECRET')

# Init db
COSMOS_URI = os.getenv('COSMOS_URI')
client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
db = client.LearnLoop

# Make authentication instance for the flask login_page
auth = OAuth(login_page)

auth.register(
    name='surfconext',
    client_id='learnloop-test.datanose.nl',
    client_secret=os.getenv('SURFCONEXT_CLIENT_SECRET'),
    server_metadata_url='https://connect.test.surfconext.nl/.well-known/openid-configuration', #TODO: change for productin env
    client_kwargs={'scope': 'openid'}
)


@login_page.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Login Page</title>
        </head>
        <body>
            <h1>Login Page</h1>
            <form action="/login">
                <input type="submit" value="Login with SURFconext">
            </form>
        </body>
    </html>
    '''


@login_page.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return auth.surfconext.authorize_redirect(redirect_uri)


def save_id_to_db(user_id):
    user = db.users.find_one({"username": user_id})
    if not user:
        db.users.insert_one({"username": user_id})
    

def save_nonce_to_db(user_id):
    nonce = secrets.token_urlsafe(16)
    db.users.update_one({'username': user_id}, {'$set': {'nonce': nonce}})
    return nonce


@login_page.route('/auth')
def authorize():
    token = auth.surfconext.authorize_access_token()

    user_id = token['userinfo']['sub']
    save_id_to_db(user_id)
    nonce = save_nonce_to_db(user_id)

    # Redirect to streamlit app
    redirect_url = f'http://localhost:8501/?nonce={nonce}'
    return redirect(redirect_url, code=302)


if __name__=="__main__":
    login_page.run(port=3000)