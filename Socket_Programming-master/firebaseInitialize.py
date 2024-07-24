
  #initialize firebase
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to your service account key from environment variable
cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
cred = credentials.Certificate(cred_path)

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
})

ref = db.reference('Logs')

# Push a new log to the database
ref.set({
    'date': '2020-05-05',
    'log': 'This is a test log'
})

# Read data from firebase
data = ref.get()
print(data)

# Update data in firebase
ref.update({
    'log': 'This is an updated log'
})