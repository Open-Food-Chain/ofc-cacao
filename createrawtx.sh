#!/bin/bash

# Define the variables
CLONE="XX_CLONE_XX"
DOCKER_ORACLE_LIMITS_NETWORK_SUBNET="172.00.101.0/24"
DATA_PATH="/var/data/komodo/coindata"
AC_NAME="OCCS"
AC_FOUNDERS=1000
AC_FOUNDERS_REWARD=5000000000000
AC_ADAPTIVEPOW=1
AC_STAKED=95
AC_REWARD=25000
AC_SUPPLY=500000000
AC_PUBKEY="038afbc819aecfb3d65acdf270f755c9279d69d4a27293f10889264b8bd6c1fae2"
AC_CC=2
ADD_NODE_1="162.55.144.64"
ADD_NODE_2="162.55.144.56"
BATCH_SMARTCHAIN_NODE_USERNAME="changeme"
BATCH_SMARTCHAIN_NODE_PASSWORD="alsochangeme"
BATCH_SMARTCHAIN_NODE_P2P_PORT=44669
BATCH_SMARTCHAIN_NODE_RPC_PORT=44670
BATCH_SMARTCHAIN_NODE_IPV4_ADDR="127.0.0.1"
THIS_NODE_RADDRESS="RGKg9LCmU5i9JL2PceLbhM9HenHmMzDU7i"
THIS_NODE_WALLET="RGKg9LCmU5i9JL2PceLbhM9HenHmMzDU7i"
THIS_NODE_PUBKEY="03bbdb8b2e5f70affe34b275899acdec3c1569b6898503fa21b40b0d537e9a2b65"
THIS_NODE_WIF="UqdsHMPfkyEaj25PBCUyKuCy9fP4EL99KRgqYjhHYTWmneaRZoYC"
HOUSEKEEPING_ADDRESS="RUf9DKpwhhykvGdmhUosBg88XmAQNjeEx2"
ORACLE_LIMITS_IPV4_ADDR="172.00.101.6"
DOCKER_KOMODO_SMARTCHAIN_NETWORK_SUBNET="172.0.0/24"

# Run the first curl command and capture the 'result' key (the raw transaction)
rawtx=$(curl --silent --user $BATCH_SMARTCHAIN_NODE_USERNAME:$BATCH_SMARTCHAIN_NODE_PASSWORD \
--data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "createrawtransaction", "params": [[{"txid":"bd99454505a6957fac0d997b4c77f95f62fe8437078ab2fe20a3e0b24d2ead32", "vout":0}], {"RGKg9LCmU5i9JL2PceLbhM9HenHmMzDU7i":523.99975} ]}' \
-H 'content-type: text/plain;' \
http://$BATCH_SMARTCHAIN_NODE_IPV4_ADDR:$BATCH_SMARTCHAIN_NODE_RPC_PORT/ | jq -r '.result')

# Run the second curl command using the captured raw transaction
curl --user $BATCH_SMARTCHAIN_NODE_USERNAME:$BATCH_SMARTCHAIN_NODE_PASSWORD \
--data-binary "{\"jsonrpc\": \"1.0\", \"id\":\"curltest\", \"method\": \"signrawtransaction\", \"params\": [\"$rawtx\"]}" \
-H 'content-type: text/plain;' \
http://$BATCH_SMARTCHAIN_NODE_IPV4_ADDR:$BATCH_SMARTCHAIN_NODE_RPC_PORT/
