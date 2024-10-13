from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
import re
from dotenv import load_dotenv

# This line is crucial; it loads the variables from .env
load_dotenv()  

app = Flask(__name__)

# Load environment variables
flask_app_url = os.getenv('FLASK_APP_URL')
flask_port = os.getenv('FLASK_PORT')
mongodb_url = os.getenv('MONGODB_URL')
mongodb_port = os.getenv('MONGODB_PORT')
mongodb_database = os.getenv('MONGODB_DATABASE')

print("url")
print(flask_app_url)

# MongoDB setup
client = MongoClient(f'{mongodb_url}:{mongodb_port}')  # Adjust as needed
db = client[mongodb_database]

print(client)

@app.route('/')
def index():
    # Example operation: count documents in a collection
    #count = db.my_collection.count_documents({})
    return jsonify({"message": "Connected to flask"})


@app.route('/addorg', methods=['POST'])
def add_org():
    collection = db['organizations']

    data = request.json
    name = data.get('name')
    pubkey = data.get('pubkey')
    raddress = data.get('raddress')

    # Validation checks
    if not all([name, pubkey, raddress]):
        return jsonify({'error': 'Missing data'}), 400

    if not (re.match(r'^02[0-9A-Fa-f]{64}$', pubkey) and re.match(r'^R[0-9A-Za-z]{33}$', raddress)):
        return jsonify({'error': 'Invalid data format'}), 400

    # Insert into MongoDB
    collection.insert_one({'name': name, 'pubkey': pubkey, 'raddress': raddress})
    return jsonify({'message': 'Organization added successfully'}), 201

@app.route('/getorg/<raddress>', methods=['GET'])
def get_org(raddress):
    collection = db['organizations']

    if not raddress:
        return jsonify({'error': 'raddress is required'}), 400

    org = collection.find_one({'raddress': raddress})

    if org:
        org.pop('_id', None)  # Remove the MongoDB _id field
        return jsonify(org)
    else:
        return jsonify({'error': 'Organization not found'}), 404

@app.route('/addbatch', methods=['POST'])
def add_batch():
    collection = db['batch']
    data = request.json

    raddress = data.get('raddress')
    pubkey = data.get('pubkey')
    org_raddress = data.get('org-raddress')

    # Validation checks
    if not all([raddress, pubkey, org_raddress]):
        return jsonify({'error': 'Missing required data'}), 400

    #if not (re.match(r'^R[0-9A-Za-z]{33}$', raddress) and 
    #        re.match(r'^02[0-9A-Fa-f]{64}$', pubkey) and 
    #        re.match(r'^R[0-9A-Za-z]{33}$', org_raddress)):
    #    return jsonify({'error': 'Invalid data format'}), 400

    # Insert into MongoDB
    collection.insert_one(data)
    return jsonify({'message': 'Batch added successfully'}), 201

@app.route('/getbatches/<org_raddress>', methods=['GET'])
def get_batches(org_raddress):
    collection = db['batch']
    
    if not org_raddress:
        return jsonify({'error': 'org-raddress is required'}), 400

    batches = list(collection.find({'org-raddress': org_raddress}))

    for batch in batches:
        batch.pop('_id', None)  # Remove the MongoDB _id field

    return jsonify(batches)

@app.route('/getallbatches', methods=['GET'])
def get_all_batches():
    collection = db['batch']
    batches = list(collection.find({}))

    for batch in batches:
        batch.pop('_id', None)  # Remove the MongoDB _id field

    return jsonify(batches)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    #app.run(debug=True)
