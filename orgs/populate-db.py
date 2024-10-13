import random
import string
import datetime
import os
import requests

from dotenv import load_dotenv

load_dotenv()  # Load environment variables

from pymongo import MongoClient

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
    for _ in range(num_batches):
        batch = {
            "anfp": random_digits(8),  # Assuming this should be digits only
            "dfp-2": random_string(16),
            "bnfp": random_digits(6),
            "pds": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "pde": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "jds": random.randint(1, 10),
            "jde": random.randint(1, 10),
            "bbd": str(random_date(datetime.date(2020, 1, 1), datetime.date(2020, 12, 31))),
            "pc": random_string(2),
            "pl": { "value":random_string(7), "hash":True},
            "rmn": random_digits(8),
            "pon": random_digits(6),
            "pop": random_digits(3),
            "mass": round(random.uniform(0.5, 2.0), 1),
            "integrity_details": None,
            "percentage": None
        }
        batches.append(batch)
    
    return batches

def insert_many_batches(batch):
    #api_url = os.getenv('IMPORT_API_HOST') + ":" + os.getenv('IMPORT_API_PORT')  # Replace with your actual URL
    
    api_url = "https://api.servinformacion.occs.openfoodchain.org/" #"https://api.mpf.occs.openfoodchain.org/" 

    collection_name = "farmer-data"
    
    response = requests.post(api_url + f'/add/farmer-data', json=batch)

    return response

batches = generate_test_batches(1)

batch = {
    "informacion_cacaocultorP4_documento":"17321676",
    "informacion_cacaocultorp10_segundo_apellido":"Valencia",
    "fecha_venta": "2022-12-12",
    "unidad":"2",
    "KEY": 
        { "value": "uuid:ecc15981-0d0f-44ff-b640-d5bd5a57c647",
          "unique": True
        }
}


#{"batchId":{"double_hash":True,"unique":True,"value":"#FARMER_NATIONAL_ID:NP-123456|#PURCHASE_DATE:01/16/2024"},"buyer":"JK Cooperatives","buyerId":"aa903a24-e6d4-495d-b57c-7c9ebdf0a7c8","cacaoType":"Organic","farmerFriendlyName":"manifoldcamera806","farmerId":"ad22e448-8fec-40f8-a943-3142f572c3e5","farmerNationalId":{"double_hash":True,"lookup":True,"value":"NP-123456"},"integrity_details":None,"isPremiumPaid":True,"moisture":10,"purchasedAt":"01/16/2024","quality":"dry_grains_seeds","quantity":100,"quantityUnit":{"abbvr":"g","name":"Gram"},"recordType":"BATCH_REGISTRATION","varieties":["CRIN TC-1"]}

#for batch in batches:
ret = insert_many_batches(batch)
print(ret.text)
