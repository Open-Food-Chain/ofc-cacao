from komodo_py.node_rpc import NodeRpc
from komodo_py.wallet import WalletInterface

from scraper import Scraper
from oracles_manager import OraclesManager

import os
from dotenv import load_dotenv

load_dotenv()

seed = os.getenv('SEED')
collections = os.getenv('COLLECTIONS').split(',')

user_name = os.getenv('BATCH_SMARTCHAIN_NODE_USERNAME')
password = os.getenv('BATCH_SMARTCHAIN_NODE_PASSWORD')
rpc_port = int(os.getenv('BATCH_SMARTCHAIN_NODE_RPC_PORT'))
private_key = os.getenv('THIS_NODE_WIF')
address = os.getenv('THIS_NODE_RADDRESS')
pubkey = os.getenv('THIS_NODE_PUBKEY')

ip_address = os.getenv('BATCH_SMARTCHAIN_NODE_IPV4_ADDR')

explorer_url = os.getenv('EXPLORER_URL')

org_name = os.getenv('ORG_NAME')

# Example usage of the Scraper class
if __name__ == "__main__":
	# Assuming 'node' should be a string URL or similar identifier for this example
	example_node = NodeRpc(user_name, password, rpc_port, private_key, ip_address)
	wal_in = WalletInterface(example_node, seed, True)
	or_man = OraclesManager(wal_in, org_name)
	scraper = Scraper(node=example_node, explorer_url=explorer_url, oracle_manager=or_man, collections=collections)

	block = scraper.scan_blocks()

	print(f"Scraper initialized with node: {block}")
