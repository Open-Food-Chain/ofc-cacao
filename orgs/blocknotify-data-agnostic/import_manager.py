import requests

class ImportManager:
	def __init__(self, base_url, port, collections):
		self.base_url = f"{base_url}:{port}"
		self.collections = collections

	def get_imports_without_integrity(self):
		"""Get all documents from all managed collections that lack integrity details."""
		all_imports = {}
		for collection_name in self.collections:
			url = f"{self.base_url}/import/{collection_name}/null_integrity"
			response = requests.get(url)

			if response.status_code == 200:
				all_imports[collection_name] = response.json()
			else:
				all_imports[collection_name] = f"Error: {response.status_code}, {response.text}"
		return all_imports

	def add_integrity_details(self, collection_name, doc_id, integrity_data):
		"""Add integrity details to a specific document."""
		if not isinstance(integrity_data, str):
			final_obj = {}
			final_obj["txlist"] = integrity_data
			final_obj["unique-addr"] = integrity_data["unique-addr"]
			final_obj['item_id'] = doc_id
			final_obj = {"integrity_data":final_obj}

			print(final_obj)

			if collection_name not in self.collections:
				raise ValueError(f"Collection {collection_name} not managed by ImportManager.")

			url = f"{self.base_url}/integrity-details/{collection_name}/{doc_id}"
			response = requests.post(url, json=final_obj)

			if response.status_code == 200:
				return f"Integrity details added successfully. New Integrity ID: {response.json().get('integrity_id')}"
			else:
				return f"Error: {response.status_code}, {response.text}"

		return "error"


	def get_first_items(self):
			"""Get the first item from each managed collection."""
			first_items = {}
			for collection_name in self.collections:
				url = f"{self.base_url}/first-item/{collection_name}"
				print(url)
				response = requests.get(url)

				if response.status_code == 200:
					first_items[collection_name] = response.json()
				else:
					first_items[collection_name] = f"Error: {response.status_code}, {response.text}"
			return first_items

class ImportManInterface:
	def __init__(self, base_url, port, collections):
		self.import_manager = ImportManager(base_url, port, collections)

	def get_imports_without_integrity(self):
		"""Get all documents from a collection that lack integrity details."""
		return self.import_manager.get_imports_without_integrity()

	def add_integrity_details(self, collection_name, doc_id, integrity_data):
		"""Update integrity details of a specific document."""
		return self.import_manager.add_integrity_details(collection_name, doc_id, integrity_data)

	def get_first_items(self):
		"""Get the first item from each collection managed by the ImportManager."""
		return self.import_manager.get_first_items()
