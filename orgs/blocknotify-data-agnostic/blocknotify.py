from blocknotify.komodo_py.transaction import TxInterface
from blocknotify.komodo_py.explorer import Explorer
from blocknotify.komodo_py.wallet import WalletInterface
from blocknotify.komodo_py.node_rpc import NodeRpc

from ecpy.curves import Curve, Point
import hashlib
import ecdsa
import time
import threading
import json

from blocknotify.wallet_manager import WalManInterface
from blocknotify.object_parser import ObjectParser
from blocknotify.chain_api_manager import ChainApiInterface
from blocknotify.oracles_manager import OraclesManager
from blocknotify.scraper import Scraper


class BlockNotify:
    def __init__(self, explorer_url, seed, chain_api_host, chain_api_port, collection_names, node_username, node_password, rpc_port, node_wif, node_ipv4_addr, node_raddress, node_pubkey, org_name):
        self.explorer_url = explorer_url
        self.seed = seed
        self.chain_api_host = chain_api_host
        self.chain_api_port = chain_api_port
        self.collection_names = collection_names
        self.node_username = node_username
        self.node_password = node_password
        self.rpc_port = rpc_port
        self.node_wif = node_wif
        self.node_ipv4_addr = node_ipv4_addr
        self.node_raddress = node_raddress
        self.node_pubkey = node_pubkey
        self.org_name = org_name
        self.init_blocknotify()

    def get_health(self):
        rpc_res = self.node_rpc.get_balance(None)

        return rpc_res

    def init_blocknotify(self):
        print("START INIT")
        self.node_rpc = NodeRpc(self.node_username, self.node_password, self.rpc_port, self.node_wif, self.node_ipv4_addr)
        self.wal_in = WalletInterface(self.node_rpc, self.seed, True)
        print("get wallet info:")
        print("pubkey:")
        print(self.wal_in.get_public_key())
        print("privkey:")
        print(self.wal_in.get_wif())
        print("address:")
        print(self.wal_in.get_address())
        self.chain_api_manager = ChainApiInterface(self.chain_api_host, self.chain_api_port)

    def run_scraper(self, collection_names):
        def scraper_routine():
            try:
                or_man = OraclesManager(self.wal_in, self.org_name)
                scraper = Scraper(node=self.node_rpc, explorer_url=self.explorer_url, oracle_manager=or_man, collections=collection_names)
                
                while True:
                    block = scraper.scan_blocks()
                    time.sleep(600)  # Sleeps for 10 minutes
            except json.JSONDecodeError as e:
                return f"error: {e}"

        # Start the scraper routine in a new thread
        thread = threading.Thread(target=scraper_routine)
        thread.start()
        return thread  # Optional: return the thread object if you need to control it later


    def get_wals(self, first_items, wal_in, node, collection_name):
        to_remove = ["integrity_details", "id", "created_at", "raw_json", "bnfp", "_id"]
        all_wall_man = {}

        if isinstance(first_items, dict):
            or_man = OraclesManager(wal_in, self.org_name)
            
            print("check " + str(first_items))
            all_wall_man[collection_name] = WalManInterface(wal_in, self.explorer_url, first_items, to_remove, or_man ,collection=collection_name)
        
        return all_wall_man

    def send_batch(self, item, collection_name):
        print("start send")
        self.all_wall_man = self.get_wals(item, self.wal_in, self.node_rpc, collection_name)
        
        print("end get wals")

        obj_parser = ObjectParser()
        

        tx_obj, unique_attribute = obj_parser.preprocess_save(item)
        
        print("parse end")
        tx_obj = obj_parser.parse_obj(tx_obj)
        print(self.all_wall_man)
        

        wal_man = self.all_wall_man.get(collection_name, None)
        if wal_man:
            ret = wal_man.send_batch_transaction(tx_obj, unique_attribute, collection_name)
            return ret
        else:
            return "Wallet manager not found for the specified collection."
