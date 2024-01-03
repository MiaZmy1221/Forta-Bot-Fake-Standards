# Fake Standards

## Description

This agent detects transactions ERC-1967 fake standards

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

- 0x2325f3a51f87d80932224ef121f7884c9b1812b22a061979df5331b9caad43d2 in Ethereum (Proxy: 0x407f5490cfa4cba715cb93645c988b504fcf0331; Logic Contract at Storage: 0xc1e97d3fc2810577289ee35e895a4f0e59481700; Real Logic Contract: 0x4674f9cf8fce3e9ff332015a0f0859baa60c2ded.)
