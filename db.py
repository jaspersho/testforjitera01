import firebase_admin as db
import json
from firebase_admin import credentials
from firebase_admin import firestore
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Authenticate to the database
cred = credentials.Certificate("firestickveteranapplication-firebase-adminsdk-ie9uk-879eb89616.json")
db.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# endpoint to grab the veterans under each caregiver, enter the caregiver's email in the request header
@app.route('/get_Caregivers_Veterans/<string:email>', methods=['GET'])
def get_caregivers_veterans(email):
    caregivers = db.collection('Users')
    veterans = []
    id = None

    for caregiver in caregivers.get():
        if caregiver.get('email') == email:
            id = caregiver.id

    parent_doc_ref = db.collection('Users').document(id)

    subcollection_ref = parent_doc_ref.collection('Veterans')

    # Get all documents in the subcollection
    subcollection_docs = subcollection_ref.get()

    # Retrieve data from the document
    for doc in subcollection_docs:
        veterans.append({'id':doc.id, 'data':doc.to_dict()})
    return jsonify({'veterans':veterans})

# endpoint to grab each veteran's tasks, enter the veteran's email in the request header
@app.route('/get_Veterans_Tasks/<string:email>', methods=['GET'])
def getVeteransTasks(email):
    users_ref = db.collection('Users')
    documents = users_ref.get()
    data_list = []

    for doc in documents:
        if doc.get('email') == email:
            email = doc.get('email')
            id = doc.id
    
    tasks_ref = users_ref.document(id).collection('Tasks')
    tasks_docs = tasks_ref.get()

    for doc in tasks_docs:
        data = doc.to_dict()
        data_list.append({'Task_Data': data})
           
    return jsonify(data_list)

# login endpoint, enter the username and password of the caregiver/veteran in the request body
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    users_ref = db.collection('Users')
    users_docs = users_ref.get()

    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "No username and/or password provided"}), 401
    
    username = data['username']
    password = data['password']

    for doc in users_docs:
        if doc.get('username')==username and doc.get('password')==password:
            if  doc.get('flag') == True:
                return jsonify({"message": "Logged in as Veteran"}), 200
            else:
                return jsonify({"messaga": "Logged in as Caregiver"}), 200
            
    return jsonify({"error": "Invalid username or password"}), 401



if __name__ == '__main__':
    app.run(debug=True)
