from pathlib import Path
import json


class AbstractModel:
    def __init__(self, layer1, layer2):
        self._blacklists = [
            # ETH
            int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
            # USDC
            int("0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8", 16),
            # USDT
            int("0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8", 16),
            # DAI
            int("0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3", 16),
            # WBTC
            int("0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac", 16),
        ]
        self._whitelists = [
            # BRIQ
            int("0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672", 16),
        ]
        self._layer1 = layer1
        self._layer2 = layer2

    def run(self):
        raise NotImplementedError

    @classmethod
    def from_json(cls, layer1_path, layer2_path):
        with open(layer1_path, 'r') as file_instance:
            layer1 = json.load(file_instance)
        with open(layer2_path, 'r') as file_instance:
            layer2 = json.load(file_instance)
        return cls(layer1, layer2)
