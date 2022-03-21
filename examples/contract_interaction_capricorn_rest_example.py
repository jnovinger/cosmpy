# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

""" Capricorn REST example of ERC1155 contract deployment and interaction """

import inspect
import os
from pathlib import Path
from typing import Any, Dict

from cosmpy.clients.crypto import CosmosCrypto
from cosmpy.clients.ledger import CosmosLedger

# ID and amount of tokens to be minted in contract
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin

TOKEN_ID = "680564733841876926926749214863536422912"
AMOUNT = "1"

# Path to smart contract
CUR_PATH = os.path.dirname(inspect.getfile(inspect.currentframe()))  # type: ignore
CONTRACT_FILENAME = Path(os.path.join(CUR_PATH, "..", "contracts", "cw_erc1155.wasm"))


# Node config
DENOM = "atestfet"
REST_ENDPOINT_ADDRESS = "https://rest-capricorn.fetch.ai:443"
FAUCET_URL = "https://faucet-capricorn.t-v2-london-c.fetch-ai.com"
CHAIN_ID = "capricorn-1"
PREFIX = "fetch"
MINIMUM_GAS_PRICE = Coin(denom=DENOM, amount=str(500000000000))


ledger = CosmosLedger(
    chain_id=CHAIN_ID,
    rest_node_address=REST_ENDPOINT_ADDRESS,
    minimum_gas_price=MINIMUM_GAS_PRICE,
    faucet_url=FAUCET_URL,
)

sender_crypto = CosmosCrypto(prefix=PREFIX)

# Refill sender's balance from faucet
ledger.ensure_funds([sender_crypto.get_address()])

code_id, _ = ledger.deploy_contract(sender_crypto, CONTRACT_FILENAME)
print(f"Code ID: {code_id}")

init_msg: Dict[str, Any] = {}
contract_address, _ = ledger.instantiate_contract(
    sender_crypto, code_id, init_msg, "some_label"
)
print(f"Contract address: {contract_address}")


# Create token with ID TOKEN_ID
create_single_msg = {
    "create_single": {
        "item_owner": sender_crypto.get_address(),
        "id": TOKEN_ID,
        "path": "some_path",
    }
}
ledger.execute_contract(sender_crypto, contract_address, create_single_msg)
print(f"Created token with ID {TOKEN_ID}")

# Mint 1 token with ID TOKEN_ID and give it to validator
mint_single_msg = {
    "mint_single": {
        "to_address": sender_crypto.get_address(),
        "id": TOKEN_ID,
        "supply": AMOUNT,
        "data": "some_data",
    },
}
response = ledger.execute_contract(sender_crypto, contract_address, mint_single_msg)
print(f"Minted 1 token with ID {TOKEN_ID}")

# Query validator's balance of token TOKEN_ID
msg = {
    "balance": {
        "address": sender_crypto.get_address(),
        "id": TOKEN_ID,
    }
}
res = ledger.query_contract_state(contract_address, msg)

# Check if balance of token with ID TOKEN_ID of validator is correct
assert res["balance"] == AMOUNT
print("All done!")
