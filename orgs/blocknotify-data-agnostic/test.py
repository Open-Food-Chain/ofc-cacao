from komodo_py.transaction import TxInterface
from komodo_py.explorer import Explorer
from komodo_py.wallet import WalletInterface
from komodo_py.node_rpc import NodeRpc

from ecpy.curves     import Curve,Point
import hashlib
import ecdsa
import time

from wallet_manager import WalManInterface
from object_parser import ObjectParser
from import_manager import ImportManInterface
from chain_api_manager import ChainApiInterface
from oracles_manager import OraclesManager
from scraper import Scraper

import os
from dotenv import load_dotenv

load_dotenv()

# Reading environment variables
explorer_url = os.getenv('EXPLORER_URL')
seed = os.getenv('SEED')
import_api_host = os.getenv('IMPORT_API_HOST')
import_api_port = int(os.getenv('IMPORT_API_PORT'))
chain_api_host = os.getenv('CHAIN_API_HOST')
chain_api_port = int(os.getenv('CHAIN_API_PORT'))
collections = os.getenv('COLLECTIONS').split(',')  # Assuming 'collections' is a comma-separated list
min_utxos = int(os.getenv('MIN_UTXOS'))
min_balance = int(os.getenv('MIN_BALANCE'))

user_name = os.getenv('BATCH_SMARTCHAIN_NODE_USERNAME')
password = os.getenv('BATCH_SMARTCHAIN_NODE_PASSWORD')
rpc_port = int(os.getenv('BATCH_SMARTCHAIN_NODE_RPC_PORT'))
private_key = os.getenv('THIS_NODE_WIF')
address = os.getenv('THIS_NODE_RADDRESS')
pubkey = os.getenv('THIS_NODE_PUBKEY')

ip_address = os.getenv('BATCH_SMARTCHAIN_NODE_IPV4_ADDR')
org_name = os.getenv('ORG_NAME')


def check_env(wal_in):
    print("test")
    err = False

    addy =  wal_in.get_address()
    pub = wal_in.get_public_key()
    wif = wal_in.get_wif()

    if not addy == address:
        print("Address in the env is not correct")
        print("It should be: ")
        print(addy)
        err = True

    if not pub == pubkey:
        print("Pubkey in the env is not correct")
        print("It should be: ")
        print(pub)    
        err = True

    if not wif == private_key:
        print("Privkey in the env is not correct")
        print("It should be: ")
        print(wif)    
        err = True   

    if err == True:
        exit()

def get_wals(import_manager, wal_in, node):
    first_items = import_manager.get_first_items()
    to_remove = ["integrity_details", "id", "created_at", "raw_json", "bnfp", "_id"]
    all_wall_man = {}

    for collection_name, test_batch in first_items.items():
        if isinstance(test_batch, dict):  # Ensure that test_batch is a dictionary
            or_man = OraclesManager(wal_in, org_name)
            all_wall_man[collection_name] = WalManInterface(wal_in, explorer_url, test_batch, to_remove, or_man, collection_name)
            scraper = Scraper(node=node, explorer_url=explorer_url, oracle_manager=or_man, collections=[collection_name])
            block = scraper.scan_blocks()

    return all_wall_man


def init_blocknotify(explorer_url, seed, import_api_host, import_api_port, chain_api_host, chain_api_port, collection_names):
    node_rpc = NodeRpc(user_name, password, rpc_port, private_key, ip_address)

    wal_in = WalletInterface(node_rpc, seed, True)


    import_man_interface = ImportManInterface(import_api_host, import_api_port, collection_names)  
    chain_api_manager = ChainApiInterface(chain_api_host, chain_api_port)
    all_wall_man = get_wals(import_man_interface, wal_in, node_rpc)



    res = chain_api_manager.check_org(wal_in.get_address())

    
    for name in all_wall_man:
        all_wall_man[name].start_utxo_manager(min_utxos, min_balance)

    return wal_in, import_man_interface, all_wall_man, chain_api_manager



def main_loop_blocknotify(wal_in, import_man_interface, all_wall_man, chain_api_manager):
    items_without_integrity = import_man_interface.get_imports_without_integrity()
    obj_parser = ObjectParser()

    if len(all_wall_man) == 0:
        return "no items try later"

    for collection_name, items in items_without_integrity.items():
        print(collection_name)
        print(items)
        wal_man = all_wall_man[collection_name]
        for item in items:
            print(item)
            
            tx_obj, unique_attribute = obj_parser.preprocess_save(item)

            if unique_attribute:
                tx_obj = obj_parser.parse_obj(tx_obj)
                
                print(tx_obj)
                print(unique_attribute)
                ret = wal_man.send_batch_transaction(tx_obj, unique_attribute, collection_name)
                print("int details: ")
                print(ret)
                if not (isinstance(ret, str )):
                    update_integrity = import_man_interface.add_integrity_details(collection_name, item['_id'], ret)
                    res = chain_api_manager.add_batch(ret["unique-addr"], ret["unique-pub"], wal_in.get_address(), item)
                    print(update_integrity)
                #    print("chain manager: " + str(res))
                else:
                    time.sleep(30)

            else:
                print("missing unique attribute ")
        
    for wal in all_wall_man:
        all_wall_man[wal].stop_utxo_manager()

    return "sucses"


def send_batch(item, collection_name):
    obj_parser = ObjectParser()
    tx_obj, unique_attribute = obj_parser.preprocess_save(item)
    tx_obj, unique_attribute = obj_parser.parse_obj(tx_obj)
    ret = wal_man.send_batch_transaction(tx_obj, unique_attribute, collection_name)
    return ret

#explorer = Explorer(explorer_url)



wal_in, import_man_interface, all_wall_man, chain_api_manager = init_blocknotify(explorer_url, seed, import_api_host, import_api_port,  chain_api_host, chain_api_port, collections)

check_env(wal_in)

ret = main_loop_blocknotify(wal_in, import_man_interface, all_wall_man, chain_api_manager)

print(ret)

print("exit with")
print("#########")
#print(ret)
print("tegar is cool")