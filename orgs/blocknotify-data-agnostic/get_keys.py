from komodo_py.wallet import WalletInterface
from komodo_py.explorer import Explorer

import os
from dotenv import load_dotenv

load_dotenv()

seed = os.getenv('SEED')

print(seed)

explorer_url = os.getenv('EXPLORER_URL')

explorer = Explorer(explorer_url)

wal_in = WalletInterface(explorer, seed, True)

print("get addy")
print(wal_in.get_address())
print("get pub key")
print(wal_in.get_public_key())
print("get wif")
print(wal_in.get_wif())
