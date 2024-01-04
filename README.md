# Fake Standards 

## Description

This agent identifies instances of fake standards implementation in transactions. 

To achieve this, the bot actively monitors all newly created contracts, evaluating whether each new contract is a proxy contract that implements the ERC-1967 standard. 

For identified proxy contracts, the bot initiates the process by retrieving the logic contract, which is expected to be stored in a fixed storage slot "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc," as per the [ERC-1967 proxy contract pattern](https://eips.ethereum.org/EIPS/eip-1967). 

Subsequently, utilizing a simulation-based approach, the bot extracts the genuine logic contract invoked by the proxy contract when executing its proxied functions. 

In cases where the logic contracts do not align, the bot issues an alert to highlight the presence of a fake standards implementation problem.

## Configuration

To simulate the transaction, the [Alchemy API Key](https://dashboard.alchemy.com) is used. Please set the variable "API_KEY" with your api key in the "agent.py" and "agent_test.py". 

## Supported Chains

- Ethereum
- Polygon
- BNB
- Optimism

## Alerts

Describe each of the type of alerts fired by this agent

- FORTA-1
  - Fired when a transaction creating a proxy contract, which triggers a fake standards problem
  - Severity is always set to "high" (mention any conditions where it could be something else)

## Test Data

The agent behaviour can be verified with the following transactions:

```bash
$ npm run tx 0x2325f3a51f87d80932224ef121f7884c9b1812b22a061979df5331b9caad43d2
```

The result should be a finding of the fake standards implementation.
```js
{
  "name": "Fake Standard Alert",
  "description": "Detected Fake Standard - Proxy: 0x407f5490cfa4cba715cb93645c988b504fcf0331; Logic Contract at Storage: 0xc1e97d3fc2810577289ee35e895a4f0e59481700; Real Logic Contract: 0x4674f9cf8fce3e9ff332015a0f0859baa60c2ded",
  "alertId": "FORTA-1",
  "protocol": "ethereum",
  "severity": "High",
  "type": "Suspicious",
  "metadata": {
    "proxy_contracct": "0x407f5490cfa4cba715cb93645c988b504fcf0331",
    "logic_in_storage": "0xc1e97d3fc2810577289ee35e895a4f0e59481700",
    "real_logic": "0x4674f9cf8fce3e9ff332015a0f0859baa60c2ded"
  },
  "addresses": [],
  "labels": [],
  "uniqueKey": "",
  "source": {},
  "timestamp": "2024-01-03 23:50:28.186196"
}
```

