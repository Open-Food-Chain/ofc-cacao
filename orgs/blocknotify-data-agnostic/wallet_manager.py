from blocknotify.komodo_py.transaction import TxInterface
from blocknotify.komodo_py.explorer import Explorer
from blocknotify.komodo_py.wallet import WalletInterface

from ecpy.curves     import Curve,Point
import hashlib
import ecdsa
import multiprocessing as mp
import asyncio
import re

class UtxoManager:
	def __init__(self, org_wal, key_wallets, min_utxos, min_balance):
		self.org_wal = org_wal
		self.wallet_manager = key_wallets
		self.min_utxos = min_utxos
		self.funding_coroutine = None
		self.stop_event = None


	async def _fund_offline_wallets(self):
		# Original implementation of fund_offline_wallets
		to_addrs = []
		amounts = []

		for key in self.key_wallets:
			if len(self.key_wallets[key].get_utxos()) < self.min_utxos or self.key_wallets[key].get_balance() < self.min_balance:
				to_addrs.append(self.key_wallets[key].get_address())
				amounts.append(100)

		if len(to_addrs) != 0:
			txid = self.org_wal.send_tx_force(to_addrs, amounts)["txid"]
			return txid

		return "fully funded"

	async def fund_offline_wallets(self):
		# Pre-processing or additional checks
		print("Starting the process to fund offline wallets.")

		# Call the original (now renamed) _fund_offline_wallets method
		result = self._fund_offline_wallets()

		# Post-processing or additional actions
		if result == "fully funded":
			return "All wallets are fully funded."
		else:
			return f"Transaction ID of funding: {result}"

		return result

	async def start_funding_loop(self):
		while True:
			await self.fund_offline_wallets()
			await asyncio.sleep(60)

	def start_funding(self):
		pool = mp.Pool(mp.cpu_count())

		# Create a stop event
		self.stop_event = mp.Event()

		res = pool.apply_async(self.start_funding_loop, (self.stop_event))
		self.funding_coroutine = pool


	def stop_funding(self):
		if self.funding_coroutine is not None:
			try:
				self.stop_event.set()

			finally:
				self.funding_coroutine.close()
				self.funding_coroutine.join()
				self.funding_coroutine = None


class WalletManager:
	def __init__(self, org_wal, ex_url, batch_obj, keys_to_remove, oracle_manager=None, collection=""):
		self.ex_url = ex_url
		self.org_wal = org_wal 
		self.batch_obj = batch_obj
		print("start")
		self.sign_key = org_wal.get_sign_key()
		print("clean")
		self.clean_batch_obj = self.remove_keys_from_json_object(keys_to_remove)
		print("get walz")
		self.key_wallets = self.get_wallets()

		print("next")
		self.utxo_manager = None
		self.oracle_manager = oracle_manager
		
		print("check 1")
		if not self.oracle_manager == None:
			print("check 1")

			key_addr = {}

			for field in self.key_wallets:
				key_addr[field] = self.key_wallets[field].get_address()

			self.oracle_manager.check_and_update_address_book(self.key_wallets, key_addr, collection)
			print("wallet made")

	def hexstring_to_bytearray(self, hexstring):
		# Remove '-' characters from the hex string
		hexstring = hexstring.replace('-', '')
		print(hexstring)
		try:
			# Convert the cleaned hex string to bytes
			byte_array = bytes.fromhex(hexstring)
			return byte_array
		except ValueError:
			# Handle invalid hex input
			return None

	def get_wallet_address(self, string):
		if (self.is_hex_string(string) and len(string) > 15):
			string = self.hexstring_to_bytearray(string)
		else:
			string = string.encode('utf-8')

		sig = self.sign_key.sign_digest_deterministic(string, hashfunc=hashlib.sha256, sigencode = ecdsa.util.sigencode_der_canonize)
		return sig


	def encode_base58(self, input_data):
		ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

		# Check if input_data is a hex string and convert to byte buffer if necessary
		if isinstance(input_data, str):
			# Convert hex string to byte buffer
			buffer = bytes.fromhex(input_data)
		elif isinstance(input_data, bytes):
			buffer = input_data
		else:
			raise TypeError("Input must be a hex string or bytes")

		# Convert the buffer to a list of integers for easier processing
		digits = [0]
		for byte in buffer:
			carry = byte
			for i in range(len(digits)):
				carry += digits[i] << 8
				digits[i] = carry % 58
				carry //= 58
			while carry > 0:
				digits.append(carry % 58)
				carry //= 58

		# Count leading zeros in buffer
		zero_count = 0
		for byte in buffer:
			if byte == 0:
				zero_count += 1
			else:
				break

		# Convert digits to Base58 string
		encoded = ''.join(ALPHABET[d] for d in reversed(digits))

		# Add leading zeros
		return ALPHABET[0] * zero_count + encoded




	def get_wallets(self):
		name_and_wal = {}

		for key in self.clean_batch_obj:
			print(key)
			# Hash the key with SHA-256
			hashed_key = hashlib.sha256(key.encode()).hexdigest()
			
			print(hashed_key)

			new_seed = self.encode_base58(hashed_key)

			print(new_seed)

			explorer = Explorer(self.ex_url)

			print("base stats")

			new_wallet = WalletInterface(explorer, new_seed)
			name_and_wal[key] = new_wallet
			print(new_seed)

		return name_and_wal

	def remove_keys_from_json_object(self, keys_to_remove):
		new_obj = self.batch_obj.copy()  # Create a shallow copy of the original dictionary
		for key in keys_to_remove:
			new_obj.pop(key, None)  # Remove the key if it exists
		return new_obj


	def create_batch_address(self, batch_value ):
		new_seed = self.encode_base58(self.get_wallet_address(batch_value))
		explorer = Explorer(self.ex_url)
		new_wallet = WalletInterface(explorer, new_seed)
		return new_wallet.get_address(), new_wallet.get_public_key()

	def _fund_offline_wallets(self):
		# Original implementation of fund_offline_wallets
		to_addrs = []
		amounts = []

		print(self.key_wallets)


		for key in self.key_wallets:

			print(self.key_wallets[key].get_utxos())
			print(to_addrs)
			print(amounts)
			print(self.key_wallets[key].get_address())

			if len(self.key_wallets[key].get_utxos()) < 10:
				to_addrs.append(self.key_wallets[key].get_address())
				amounts.append(1)

		if len(to_addrs) != 0:
			print("try to send from:")
			print(self.org_wal.get_address())
			res = self.org_wal.send_tx_force(to_addrs, amounts)['txid']

			print(res)
			return txid

		return "fully funded"

	def fund_offline_wallets(self):
		# Pre-processing or additional checks
		print("Starting the process to fund offline wallets.")

		# Call the original (now renamed) _fund_offline_wallets method
		result = self._fund_offline_wallets()

		# Post-processing or additional actions
		if result == "fully funded":
			return "All wallets are fully funded."
		else:
			return f"Transaction ID of funding: {result}"

		return result

	def is_hex_string(self, input_string):

		if isinstance(input_string, dict):
			return False
		# Define a regular expression pattern for a hexadecimal string
		hex_pattern = re.compile(r'^[0-9a-fA-F-]+$')

		# Use the re.match function to check if the input string matches the pattern
		if re.match(hex_pattern, input_string):
			return True
		else:
			return False

	def send_batch_transaction_not_flat(self, tx_obj, batch_value, marker=29185):
		print("test")
		to_addr, to_pub = self.create_batch_address(batch_value)
		tx_ids = {"unique-addr":to_addr, "unique-pub":to_pub}
		print(tx_ids)
		txid = self.org_wal.send_tx_opreturn(to_addr, tx_obj, marker)	
		tx_ids["txid"] = txid

		return tx_ids

	def collection_name_to_marker(self, collection):
		print(collection)
		# Hash the collection name using SHA-256
		hash_object = hashlib.sha256(collection.encode())
		# Get the hexadecimal digest of the hash
		hex_digest = hash_object.hexdigest()
		# Take the first 5 characters of the hex digest
		first_5_chars = hex_digest[:5]
		# Convert the hexadecimal to decimal
		decimal_representation = int(first_5_chars, 16)
		print(decimal_representation)
		return decimal_representation


	def send_batch_transaction(self, tx_obj, batch_value, collection_name):
		hexstring = self.is_hex_string(tx_obj)

		marker = self.collection_name_to_marker(collection_name)

		if not hexstring:
			return self.send_batch_transaction_flat(tx_obj, batch_value)

		return self.send_batch_transaction_not_flat(tx_obj, batch_value, marker)

	def send_batch_transaction_flat(self, tx_obj, batch_value):
		print(tx_obj)

		# Preprocessing: Remove keys with value 0
		tx_obj = {k: v for k, v in tx_obj.items() if v != [0]}

		print(tx_obj)

		# Call the original send_batch_transaction logic
		tx_ids = self._send_batch_transaction(tx_obj, batch_value)

		# Postprocessing: Check if any of the returned keys have None as value
		if any(value is None for value in tx_ids.values()):
			self.fund_offline_wallets()
			print(tx_ids)
			return "Error: Not enought utxos, funding already activated, please wait"

		return tx_ids



	def _send_batch_transaction(self, tx_obj, batch_value):
		to_addr, to_pub = self.create_batch_address(batch_value)
		tx_ids = {"unique-addr":to_addr, "unique-pub":to_pub}

		for key in self.key_wallets:
			send_addrs = []
			send_amounts = []
			
			try:
				if key in tx_obj:
					send_amounts = tx_obj[key]
			
			except ValueError:
				print("obj not complete")
				return "obj not complete"

			if send_amounts:
				if isinstance(send_amounts[0], str):
					print(send_amounts)
					print(to_addr)
					txid = self.key_wallets[key].send_tx_opreturn(to_addr, send_amounts)
					tx_ids[key] = txid

				else:
					for i in range(len(send_amounts)):
						send_addrs.append(to_addr)

					print("-- normal tx --")

					txid = self.key_wallets[key].send_tx_force(send_addrs, send_amounts)	
					tx_ids[key] = txid

		return tx_ids



	def start_utxo_manager(self, min_utxos, min_balance):
		self.utxo_manager = UtxoManager(self.org_wal, self.key_wallets, min_utxos, min_balance )
		self.utxo_manager.start_funding()
		return "sucses"

	def stop_utxo_manager(self):
		self.utxo_manager.stop_funding()
		self.utxo_manager = None
		return "sucses"

class WalManInterface:
	def __init__(self, org_wal, explorer_url, batch_obj, keys_to_remove, oracle_manager=None, collection=""):
		self.wallet_manager = WalletManager(org_wal, explorer_url, batch_obj, keys_to_remove, oracle_manager, collection)

	def fund_offline_wallets(self):
		return self.wallet_manager.fund_offline_wallets()

	def send_batch_transaction(self, tx_obj, batch_value, collection_name):
		return self.wallet_manager.send_batch_transaction(tx_obj, batch_value, collection_name)

	def start_utxo_manager(self, min_utxos, min_balance):
		return self.wallet_manager.start_utxo_manager(min_utxos, min_balance)

	def stop_utxo_manager(self):
		return self.wallet_manager.stop_utxo_manager()