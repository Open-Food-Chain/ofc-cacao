import sys
import requests
import os
from dotenv import load_dotenv

# This line is crucial; it loads the variables from .env
load_dotenv()  

base_url = f"{os.getenv('FLASK_APP_URL')}:{os.getenv('FLASK_PORT')}"


def test_home():
    url = f"{base_url}/"  # URL where your Flask app is running
    response = requests.get(url)
    print("test")
    return response.text

def test_add_org():
    url = "http://localhost:5000/addorg"  # URL where your Flask app's addorg endpoint is running
    data = {
        "name": "test2",
        "pubkey": "020293989838484848488484849485948594859485948594850948594898498898",
        "raddress": "RGKg9LCmU5i9JL2PceLbhM9HenHmMzDU7i"
    }
    response = requests.post(url, json=data)

    assert response.status_code == 201, "Expected status code 201, got {}".format(response.status_code)
    print("Add organization test passed.")

def test_get_org():
    raddress = "RVq2Fmeb9HuXShoh8SVddVKVjEckN3nRzL"
    url = f"{base_url}/getorg/{raddress}"
    response = requests.get(url)

    assert response.status_code == 200, "Expected status code 200, got {}".format(response.status_code)
    assert 'name' in response.json(), "Response does not contain 'name'"
    assert response.json()['name'] == 'test1', "Organization name does not match"
    print(response.json())

def test_add_batch():
    url = f"{base_url}/addbatch"
    data = {
        "raddress": "RMXqGFHvYf5eRPkhSnLN19bx91qrS8ys9N",
        "pubkey": "020293989838484848488484849485948594859485948594850948594898498898",
        "org-raddress": "RVq2Fmeb9HuXShoh8SVddVKVjEckN3nRzL",
        "name":"test1"
    }
    response = requests.post(url, json=data)

    assert response.status_code == 201, "Expected status code 201, got {}".format(response.status_code)
    print("Add batch test passed.")

def test_get_batches():
    org_raddress = "RVq2Fmeb9HuXShoh8SVddVKVjEckN3nRzL"
    url = f"{base_url}/getbatches/{org_raddress}"
    response = requests.get(url)

    assert response.status_code == 200, "Expected status code 200, got {}".format(response.status_code)
    assert isinstance(response.json(), list), "Response is not a list"
    print("Get batches test passed.")

def test_get_all_batches():
    url = f"{base_url}/getallbatches"
    response = requests.get(url)

    assert response.status_code == 200, "Expected status code 200, got {}".format(response.status_code)
    assert isinstance(response.json(), list), "Response is not a list"
    print("Get all batches test passed.")


if __name__ == '__main__':
    if 'home' in sys.argv:
        print(test_home())
    elif 'addorg' in sys.argv:
        test_add_org()
    elif 'getorg' in sys.argv:
        test_get_org()
    elif 'addbatch' in sys.argv:
        test_add_batch()
    elif 'getbatches' in sys.argv:
        test_get_batches()
    elif 'getallbatches' in sys.argv:
        test_get_all_batches()
    else:
        print("does not exist")