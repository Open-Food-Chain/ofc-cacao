import requests

class ChainApiManager:
    def __init__(self, app_url, port):
        self.base_url = f"http://{app_url}:{port}"

    def get_organization(self, raddress):
        url = f"{self.base_url}/getorg/{raddress}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}"

    def add_batch(self, raddress, pubkey, org_raddress, batch_data):
        url = f"{self.base_url}/addbatch"
        data = {
            "raddress": raddress,
            "pubkey": pubkey,
            "org-raddress": org_raddress
        }
        # Merging batch_data into the data dictionary

        data.update(batch_data)
        print(data)
        del data['_id']
        
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return "Batch added successfully"
        else:
            print(response.text)
            return f"Error: {response.status_code}"


class ChainApiInterface:
    def __init__(self, url, port):
        self.api_manager = ChainApiManager(url, port)

    def check_org(self, raddress):
        resp = self.api_manager.get_organization(raddress)
        if "name" in resp:
            return True

        return False


    def add_batch(self, raddress, pubkey, org_raddress, batch_data):
        return self.api_manager.add_batch(raddress, pubkey, org_raddress, batch_data)

# Example usage:
# api_manager = ChainApiManager("http://localhost", "5000")
# print(api_manager.get_organization("RVq2Fmeb9HuXShoh8SVddVKVjEckN3nRzL"))
# batch_data = {"extra_field1": "value1", "extra_field2": "value2"}
# print(api_manager.add_batch("RMXqGFHvYf5eRPkhSnLN19bx91qrS8ys9N", "020293989838484848488484849485948594859485948594850948594898498898", "RVq2Fmeb9HuXShoh8SVddVKVjEckN3nRzL", batch_data))
