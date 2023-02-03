import asyncio
import json
import sys
from pathlib import Path

from grpc import ssl_channel_credentials
from grpc.aio import secure_channel

from apibara.protocol import StreamService
from apibara.protocol.proto.stream_pb2 import DataFinality
from apibara.starknet import Block, EventFilter, Filter, felt, starknet_cursor


class Indexer:

    BRIQ_ADDRESS = felt.from_hex(
        "0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672"
    )

    ETH_ADDRESS = felt.from_hex(
        "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    )

    USDC_ADDRESS = felt.from_hex(
        "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
    )

    USDT_ADDRESS = felt.from_hex(
        "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
    )

    DAI_ADDRESS = felt.from_hex(
        "0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3",
    )

    WBTC_ADDRESS = felt.from_hex(
        "0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac",
    )

    TRANSFER_KEY = felt.from_hex(
        "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )

    TABLE = {
        felt.to_hex(BRIQ_ADDRESS): 'BRIQ',
        felt.to_hex(ETH_ADDRESS): 'ETH',
        felt.to_hex(USDC_ADDRESS): 'USDC',
        felt.to_hex(USDT_ADDRESS): 'USDT',
        felt.to_hex(DAI_ADDRESS): 'DAI',
        felt.to_hex(WBTC_ADDRESS): 'WBTC',
    }

    def __init__(self):

        service_config = json.dumps(
            {
                "methodConfig": [
                    {
                        "retryPolicy": {
                            "maxAttempts": 5,
                            "initialBackoff": "0.1s",
                            "maxBackoff": "10s",
                            "backoffMultiplier": 2,
                            "retryableStatusCodes": ["UNAVAILABLE"],
                        },
                    }
                ]
            }
        )
        max_receive_message_length = 128 * 1048576

        channel = secure_channel(
            "mainnet.starknet.a5a.ch",
            ssl_channel_credentials(),
            options=[
                ('grpc.max_receive_message_length',
                 max_receive_message_length),
                ("grpc.service_config", service_config)
            ])

        (self._client, self._stream) = StreamService(channel).stream_data()

    async def config(self, finality=DataFinality.DATA_STATUS_PENDING, batch_size=10, cursor=starknet_cursor(0), nodes=None):
        nodes = [] if nodes is None else nodes
        filter = (
            Filter()
            .with_header(weak=False)
            # .add_event(EventFilter().with_from_address(self.BRIQ_ADDRESS).with_keys([self.TRANSFER_KEY]))
            # .add_event(EventFilter().with_from_address(ether_address).with_keys([transfer_key]))
            # .add_event(EventFilter().with_from_address(usdc_address).with_keys([transfer_key]))
            # .add_event(EventFilter().with_from_address(usdt_address).with_keys([transfer_key]))
            # .add_event(EventFilter().with_from_address(dai_address).with_keys([transfer_key]))
            # .add_event(EventFilter().with_from_address(wbtc_address).with_keys([transfer_key]))
            .encode()
        )

        await self._client.configure(
            filter=filter,
            finality=finality,
            batch_size=batch_size,
            cursor=cursor,
        )

    async def run(self):
        # await self.config()

        await self._client.configure(
            filter=Filter().with_header(weak=False).encode(),
            finality=DataFinality.DATA_STATUS_PENDING,
            batch_size=10,
            cursor=starknet_cursor(0),
        )

        try:
            async for message in self._stream:
                if message.data is not None:
                    self.handle_batches(message.data.data)
        except IndexError:
            print('Indexing ends')

    def handle_batches(self, batches):
        block = Block()
        for batch in batches:
            block.ParseFromString(batch)
            self.handle_block(block)

    def handle_block(self, block):
        block_number = block.header.block_number
        print(block_number)

        if block_number > 19_560:
            raise IndexError

        for event_with_tx in block.events:
            self.handle_event(event_with_tx, block)

    def handle_event(self, event_with_tx, block):
        event = event_with_tx.event
        tx = event_with_tx.transaction

        time = block.header.timestamp.ToSeconds()
        tx_hash = felt.to_hex(tx.meta.hash)
        contract = felt.to_hex(event.from_address)
        contract_name = self.TABLE.get(contract)

        sender = felt.to_hex(event.data[0])
        recipient = felt.to_hex(event.data[1])

        value = felt.to_int(event.data[2]) + (
            felt.to_int(event.data[3]) << 128
        )
        print(value)

        #             for event_with_tx in block.events:
        #                 event = event_with_tx.event
        #                 tx = event_with_tx.transaction

        #                 time = block.header.timestamp.ToSeconds()
        #                 tx_hash = felt.to_hex(tx.meta.hash)
        #                 contract = felt.to_hex(event.from_address)
        #                 contract_name = table.get(contract)

        #                 sender = felt.to_hex(event.data[0])
        #                 recipient = felt.to_hex(event.data[1])

        #                 value = felt.to_int(event.data[2]) + (
        #                     felt.to_int(event.data[3]) << 128
        #                 )

        #                 new.append({
        #                     'contract': contract,
        #                     'name': contract_name,
        #                     'time': time,
        #                     'block': block_number,
        #                     'hash': tx_hash,
        #                     'sender': sender,
        #                     'recipient': recipient,
        #                     'value': str(value),
        #                 })

        #         data = []
        #         if path.exists():
        #             with open('briq.json', 'r') as fin:
        #                 data = json.load(fin)
        #         with open('briq.json', 'w') as fout:
        #             data.extend(new)
        #             json.dump(data, fout, indent=2)

        # with open('briq.json', 'r') as fin:
        #     data = json.load(fin)


# path = Path("./briq.json")
# data = []
# if path.exists():
#     with open('briq.json', 'r') as fin:
#         data = json.load(fin)
# START = max([row.get('block') for row in data]) + 1 if data else 0
# print(START)


# async def main():

#     briqs_address = felt.from_hex(
#         "0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672"
#     )

#     ether_address = felt.from_hex(
#         "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
#     )

#     usdc_address = felt.from_hex(
#         "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
#     )

#     usdt_address = felt.from_hex(
#         "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
#     )

#     dai_address = felt.from_hex(
#         "0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3",
#     )

#     wbtc_address = felt.from_hex(
#         "0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac",
#     )

#     transfer_key = felt.from_hex(
#         "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
#     )

#     table = {
#         felt.to_hex(briqs_address): 'BRIQ',
#         felt.to_hex(ether_address): 'ETH',
#         felt.to_hex(usdc_address): 'USDC',
#         felt.to_hex(usdt_address): 'USDT',
#         felt.to_hex(dai_address): 'DAI',
#         felt.to_hex(wbtc_address): 'WBTC',
#     }

#     channel = secure_channel("mainnet.starknet.a5a.ch",
#                              ssl_channel_credentials(),
#                              options=[
#                                  ('grpc.max_receive_message_length', 128 * 1048576),
#                                  ("grpc.service_config", GRPC_CONFIG)])

#     (client, stream) = StreamService(channel).stream_data()

#     filter = (
#         Filter()
#         .with_header(weak=True)
#         .add_event(EventFilter().with_from_address(briqs_address).with_keys([transfer_key]))
#         # .add_event(EventFilter().with_from_address(ether_address).with_keys([transfer_key]))
#         # .add_event(EventFilter().with_from_address(usdc_address).with_keys([transfer_key]))
#         # .add_event(EventFilter().with_from_address(usdt_address).with_keys([transfer_key]))
#         # .add_event(EventFilter().with_from_address(dai_address).with_keys([transfer_key]))
#         # .add_event(EventFilter().with_from_address(wbtc_address).with_keys([transfer_key]))
#         .encode()
#     )

#     await client.configure(
#         filter=filter,
#         finality=DataFinality.DATA_STATUS_PENDING,
#         batch_size=10,
#         cursor=starknet_cursor(START)
#     )


# if __name__ == "__main__":
#     asyncio.run(main())
