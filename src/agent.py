from forta_agent import get_json_rpc_url, get_chain_id, EntityType
from forta_agent import Finding, FindingType, FindingSeverity
from web3 import Web3
import rlp
import requests
import json
import time

# use your own api key from Alchemy
API_KEY_Ethereum = ""
API_KEY_Polygon = ""
API_KEY_Optimism = ""

# get web3
web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

# get the created contract
def calc_contract_address(address, nonce) -> str:
    address_bytes = bytes.fromhex(address[2:].lower())
    return Web3.toChecksumAddress(Web3.keccak(rlp.encode([address_bytes, nonce]))[-20:])

def detect_contract_creations(w3, transaction_event):
    created_contract_addresses = []

    # check the external transaction
    if transaction_event.to is None:
        nonce = transaction_event.transaction.nonce
        created_contract_address = calc_contract_address(transaction_event.from_, nonce)
        created_contract_addresses.append(created_contract_address.lower())

    # check the internal transactions/traces
    for trace in transaction_event.traces:
        if trace.type == 'create':
            if (transaction_event.from_ == trace.action.from_ or trace.action.from_ in created_contract_addresses):
                # for contracts creating other contracts, the nonce would be 1
                nonce = transaction_event.transaction.nonce if transaction_event.from_ == trace.action.from_ else 1
                created_contract_address = calc_contract_address(trace.action.from_, nonce)
                created_contract_addresses.append(created_contract_address.lower())

    return created_contract_addresses


# get storage slot at the ERC-1967 implementation slot
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
def get_logic_contract(proxy):
    return web3.eth.get_storage_at(Web3.toChecksumAddress(proxy), IMPLEMENTATION_SLOT)

# get the real called logic contract from simulating a tx and compare these two contracts
FORTA_DEVELOPER = "0xb37dd8269d2d81d8954983a9d3c67fec5e1f9837" # can be any eoa address
def config_alchemy_api_key(api_keys):
    chain_id = get_chain_id()
    if chain_id == 1:
        return "https://eth-mainnet.g.alchemy.com/v2/" + api_keys[0]
    elif chain_id == 137:
        return "https://polygon-mainnet.g.alchemy.com/v2/" + api_keys[1]
    elif chain_id == 10:
        return "https://opt-mainnet.g.alchemy.com/v2/" + api_keys[2]


def alchemy_simulate_transaction(url, proxy_contract, logic_contract):
    tries = 3
    for i in range(tries):
        try: 
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_simulateExecution",
                "params": [
                    {
                        "from": FORTA_DEVELOPER,
                        "to": proxy_contract,
                        "value": "0x0",
                        "data": "0xdeadbeef"
                    }
                ]
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            # obtain the response
            response = requests.post(url, json=payload, headers=headers)
            calls = json.loads(response.text)["result"]["calls"]

            # obtain the real logic contract
            for call in calls:
                # find the delegatecall
                if call["type"] == "DELEGATECALL" and call["from"] == proxy_contract and call["input"] == "0xdeadbeef":
                    if call["to"] == logic_contract:
                        return True, call["to"]
                    else:
                        return False, call["to"]
            return False, "No delegatecall during simulation"

        except KeyError as e:
            if i < tries - 1:
                time.sleep(1) 
                continue
            else:
                raise Exception("Alechmy simulation error:", response.text)
        break

def fake_standards(api_keys, contracts):
    findings = []

    # iterate every ERC1967 proxy contract
    for contract in contracts:
        # get storage slot at the ERC-1967 implementation slot
        logic_contract = get_logic_contract(contract)
        logic_contract = "0x" + logic_contract.hex()[26:]
        if logic_contract == "0x0000000000000000000000000000000000000000":
            continue

        # get the real called logic contract from simulating a transaction and compare these two contracts
        url = config_alchemy_api_key(api_keys)
        match, real_logic_contract = alchemy_simulate_transaction(url, contract, logic_contract)
        if not match and real_logic_contract != "":
            findings.append(Finding({
                'name': 'Fake Standard Alert',
                'description': f'Detected Fake Standard - Proxy: {contract}; Logic Contract at Storage: {logic_contract}; Real Logic Contract: {real_logic_contract}',
                'alert_id': 'FORTA-1',
                'type': FindingType.Suspicious,
                'severity': FindingSeverity.High,
                'metadata': {
                    'proxy_contracct': contract,
                    'logic_in_storage': logic_contract,
                    'real_logic': real_logic_contract,
                    'chain_id': get_chain_id(),
                }
            }))
    return findings


def handle_transaction(transaction_event):
    # get the created contract
    contracts = detect_contract_creations(web3, transaction_event)
    # if no newly created contracts, return empty findings
    api_keys = [API_KEY_Ethereum, API_KEY_Polygon, API_KEY_Optimism]
    return fake_standards(api_keys, contracts)