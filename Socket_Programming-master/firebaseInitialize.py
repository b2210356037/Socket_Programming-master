#initialize firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Path to your service account key
cred = credentials.Certificate('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'FIREBASE_DATABASE_URL'
})

ref = db.reference('Logs')

# Push a new log to the database
ref.set({
    'date': '2020-05-05',
    'log': 'This is a test log'
})

#read data from firebase
data = ref.get()
print(data)

#update data in firebase
ref.update({
    'log': 'This is an updated log'
})

