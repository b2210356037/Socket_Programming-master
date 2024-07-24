
  #initialize firebase
# firebase.py

import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from firebase_admin import firestore

# Load environment variables from .env file
load_dotenv()

# Path to your service account key from environment variable
cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
cred = credentials.Certificate(cred_path)

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()
