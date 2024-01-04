from hexbytes import HexBytes

PROXY = "0x407f5490cfa4cba715cb93645c988b504fcf0331"
IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
            

class Web3Mock:
    def __init__(self):
        self.eth = EthMock()


class EthMock:
    def __init__(self):
        self.contract = ContractMock()

    def get_storage_at(self, address, position):
        if address == PROXY and position == IMPLEMENTATION_SLOT:
            return HexBytes('0x000000000000000000000000c1e97d3fc2810577289ee35e895a4f0e59481700')
        else:
            return HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000')
 

class ContractMock:
    def __init__(self):
        self.functions = FunctionsMock()

    def __call__(self, address, *args, **kwargs):
        return self


class FunctionsMock:
    def __init__(self):
        self.return_value = None

    def call(self, *_, **__):
        return self.return_value