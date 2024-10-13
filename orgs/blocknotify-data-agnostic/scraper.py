from blocknotify.komodo_py.explorer import QueryInterface
from blocknotify.komodo_py.explorer import Explorer

import json
import hashlib

class Scraper:
	def __init__(self, node, explorer_url, oracle_manager, collections):
		self.node = node
		self.query = QueryInterface(self.node)

		self.ex = QueryInterface(Explorer(explorer_url))

		self.oracle_manager = oracle_manager

		self.type = "R"

		self.name_field = 'farmerNationalId'

		self.name_collections = collections

	def create_json_object(self, t, n, r, o):
		"""
		Creates a JSON-like dictionary object with the provided values.

		:param t: Type
		:param n: Name
		:param r: Address
		:param pk: Public Key
		:param o: Oracle ID
		:return: A dictionary structured as the given JSON object
		"""
		return {
			"t": t,
			"n": n,
			"r": r,
			"o": o
		}

	def get_block(self, height):
		return self.query.get_block(height)

	def get_opreturn_from_tx(self, full_tx):
		for vout in full_tx['vout']:
			script_hex = vout['scriptPubKey']['hex']
			if script_hex.startswith('6a'):
				return script_hex
		return None  # Return None if no OP_RETURN is found

	def get_address_from_tx(self, full_tx, marker):
		for vout in full_tx['vout']:
			if float(vout['value']) == float(marker/100000000):
				return vout['scriptPubKey']['addresses']
		return None  # Return None if no OP_RETURN is found

	def parse_opreturn(self, opreturn):
		if not opreturn.startswith('6a'):
			return "Not an OP_RETURN"

		# Remove the OP_RETURN opcode '6a'
		opreturn = opreturn[2:]

		# Check for PUSHDATA opcodes and adjust accordingly
		if opreturn.startswith('4d'):
			opreturn = opreturn[6:]  # Skip next 2 bytes for 4d (PUSHDATA2)
		else:
			opreturn = opreturn[2:]  # Skip next byte for normal cases

		# Convert from hex to ASCII
		try:
			opreturn_ascii = bytes.fromhex(opreturn).decode('utf-8')
		except ValueError as e:
			return f"Error converting hex to ASCII: {e}"

		# Attempt to parse the ASCII string as JSON
		try:
			opreturn_json = json.loads(opreturn_ascii)
		except json.JSONDecodeError as e:
			return f"Error parsing ASCII to JSON: {e}"

		return opreturn_json

	## right now this one is defined 2 times in different objects...
	def collection_name_to_marker(self, collection):
		#print(collection)
		# Hash the collection name using SHA-256
		hash_object = hashlib.sha256(collection.encode())
		# Get the hexadecimal digest of the hash
		hex_digest = hash_object.hexdigest()
		# Take the first 5 characters of the hex digest
		first_5_chars = hex_digest[:5]
		# Convert the hexadecimal to decimal
		decimal_representation = int(first_5_chars, 16)
		#print(decimal_representation)
		return decimal_representation


	def check_block_tx(self, height):
		block = self.get_block(height)

		ret = []

		for collection in self.name_collections:
			marker = self.collection_name_to_marker(collection)

			for tx in block['tx']:
				full_tx = self.ex.get_transaction(tx)

				for vout in full_tx['vout']:
					if float(vout['value']) == float(marker/100000000):

						address = self.get_address_from_tx(full_tx, marker)
						opreturn = self.get_opreturn_from_tx(full_tx)
						oracle_txid = self.oracle_manager.get_this_org_collection_addressbook(collection)
						opreturn = self.parse_opreturn(opreturn)

						to_oracle_obj = self.create_json_object(self.type, opreturn[self.name_field], address, oracle_txid)

						txid = self.oracle_manager.publish_to_addressbook_oracle(collection, to_oracle_obj)
						ret_obj = {}
						ret_obj[collection] = {}
						ret_obj[collection][tx] = txid

						ret.append(ret_obj)

		return ret

	def scan_blocks( self ):
		ret = []

		print("test")
		count = self.query.get_blockcount()
		print(count)
		print("test")
		for x in range(count-10, count):
			print(x)
			ret_obj = {}
			ret_obj[x] = self.check_block_tx(str(x))
			ret.append(ret_obj)

		return ret