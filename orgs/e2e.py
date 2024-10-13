import random
import string
import datetime
import requests
import os
import json
import subprocess
import time

from pymongo import MongoClient
from dotenv import load_dotenv

# This line is crucial; it loads the variables from .env
load_dotenv()  

def random_digits(length):
    """Generate a random string of digits with fixed length."""
    return ''.join(random.choices(string.digits, k=length))

def random_string(length):
    """Generate a random string of letters and digits with fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_date(start, end):
    """Generate a random date between `start` and `end`."""
    delta = end - start
    return start + datetime.timedelta(days=random.randint(0, delta.days))

def generate_test_batches(num_batches):
    batches = []
    uniq = []
    for _ in range(num_batches):
        batch = {
            "anfp-2": random_digits(8),  # Assuming this should be digits only
            "dfp-2": random_string(16),
            "unique-bnfp": random_digits(6),
            "pds": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "pde": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "jds": random.randint(1, 10),
            "jde": random.randint(1, 10),
            "bbd": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "pc": random_string(2),
            "pl": random_string(7),
            "rmn-2": random_digits(8),
            "pon": random_digits(6),
            "pop": random_digits(3),
            "mass": round(random.uniform(0.5, 2.0), 1),
            "integrity_details": None,
            "percentage": None
        }
        batches.append(batch)
        uniq.append(batch['unique-bnfp'])
    
    return batches, uniq

def insert_many_batches():
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost')
    mongo_port = os.getenv('MONGODB_PORT', '27018')

    # Connect to MongoDB (adjust the connection string as needed)
    client = MongoClient( mongo_url + ":" + mongo_port + "/")
    db = client["mydatabase"]  # Replace with your database name
    collection = db["batch"]   # The collection where you want to insert

    # Generate 10 random batch objects
    batches, uniq = generate_test_batches(10)

    # Insert them into the collection
    collection.insert_many(batches)
    print(f"Inserted {len(batches)} batches into the collection.")

    return uniq

def get_chain_batches():
    # Get the environment variables
    chain_api_host = os.getenv('CHAIN_API_HOST')
    print(chain_api_host)
    chain_api_port = int(os.getenv('CHAIN_API_PORT'))

    # Construct the URL for the Flask app
    url = f'http://{chain_api_host}:{chain_api_port}/getallbatches'

    try:
        # Make an HTTP GET request to the Flask app
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # You can access the response content using response.text
            return json.loads(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def check_if_exist(batches):
    uniqs = []

    for batch in batches:
        if "unique-bnfp" in batch:
            uniqs.append(batch['unique-bnfp'])


    return uniqs

def check_uniqs(import_uniqs, chain_uniqs):
    return_obj = list(import_uniqs)

    for import_uniq in import_uniqs:
        if import_uniq in chain_uniqs:
            return_obj.remove(import_uniq)

    return return_obj

def run_blocknotify():
    command = ["docker-compose", "up", "block"]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running other_script.py: {e}")

uniq = insert_many_batches()
run_blocknotify()
ret = get_chain_batches()
ret = check_if_exist(ret)
time.sleep(5)

ret = check_uniqs(uniq, ret)

if len(ret) == 0:
    print("All batches are run sucsesfully")
else:
    print("these batches failed: ")
    print(ret)
    print(str(len(ret)) + ", out of 10")
