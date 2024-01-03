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

- 0x968e60f81f3b83d6b6db4f449656acc9e5c73f50e9837d85aebb5f8f71998f67 (A ERC1967 proxy contract was created in this transaction, but there is no such a fake standards problem.)
