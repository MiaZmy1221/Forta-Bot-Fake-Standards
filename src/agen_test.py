from unittest.mock import Mock
from web3_mock import Web3Mock
from forta_agent import FindingSeverity, FindingType, create_transaction_event
from agent import handle_transaction, detect_contract_creations, IMPLEMENTATION_SLOT
import agent

w3 = Web3Mock()
# use your own api key from Alchemy
API_KEY_Ethereum = ""
API_KEY_Polygon = ""
API_KEY_Optimism = ""

# Test case: 0x2325f3a51f87d80932224ef121f7884c9b1812b22a061979df5331b9caad43d2 in Ethereum blockchain
class TestFakeStandardsAgent:
    def test_calc_contract_address(self):
        contract_address = agent.calc_contract_address("0xeed2f9bb322235338747298cad226cae9efb9a04", 936).lower()
        assert contract_address == "0x407f5490cfa4cba715cb93645c988b504fcf0331", "should be the same contract address"

    def test_detect_contract_creations(self):
        tx_event = create_transaction_event(
            {
                "from_": "0xeed2f9bb322235338747298cad226cae9efb9a04",
                "transaction": {
                    "from": "0xeed2f9bb322235338747298cad226cae9efb9a04",
                    "nonce": 936,
                },
                "traces": [],
            }
        )
        created_contract_addresses = agent.detect_contract_creations(w3, tx_event)
        assert len(created_contract_addresses) == 1
        assert created_contract_addresses[0].lower() == "0x407f5490cfa4cba715cb93645c988b504fcf0331"

    def test_get_logic_contract(self):
        proxy = "0x407f5490cfa4cba715cb93645c988b504fcf0331"
        logic = agent.get_logic_contract(proxy)
        logic = "0x" + logic.hex()[26:]
        assert logic == "0xc1e97d3fc2810577289ee35e895a4f0e59481700"

    def test_alchemy_simulate_transaction(self):
        url = agent.config_alchemy_api_key([API_KEY_Ethereum, API_KEY_Polygon, API_KEY_Optimism])
        proxy = "0x407f5490cfa4cba715cb93645c988b504fcf0331"
        logic_at_storage = "0xc1e97d3fc2810577289ee35e895a4f0e59481700"
        match_flag, real_logic = agent.alchemy_simulate_transaction(url, proxy, logic_at_storage)
        assert match_flag == False
        assert real_logic == "0x4674f9cf8fce3e9ff332015a0f0859baa60c2ded"

    def test_fake_standards(self):
        tx_event = create_transaction_event(
            {
                "from_": "0xeed2f9bb322235338747298cad226cae9efb9a04",
                "transaction": {
                    "from": "0xeed2f9bb322235338747298cad226cae9efb9a04",
                    "nonce": 936,
                },
                "traces": [],
            }
        )
        created_contract_addresses = agent.detect_contract_creations(w3, tx_event)
        findings = agent.fake_standards([API_KEY_Ethereum, API_KEY_Polygon, API_KEY_Optimism], created_contract_addresses)
        assert len(findings) == 1
        finding = findings[0]
        assert finding.name == "Fake Standard Alert"
        assert finding.metadata["proxy_contracct"] == "0x407f5490cfa4cba715cb93645c988b504fcf0331"
        assert finding.metadata["logic_in_storage"] == "0xc1e97d3fc2810577289ee35e895a4f0e59481700"
        assert finding.metadata["real_logic"] == "0x4674f9cf8fce3e9ff332015a0f0859baa60c2ded"