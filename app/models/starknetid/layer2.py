import asyncio
from decimal import Decimal
import json
import sys
import time
from pathlib import Path

from grpc import ssl_channel_credentials
from grpc.aio import secure_channel

from apibara.protocol import StreamService
from apibara.protocol.proto.stream_pb2 import DataFinality
from apibara.starknet import Block, EventFilter, Filter, felt, TransactionFilter, starknet_cursor
from apibara.starknet.filter import StateUpdateFilter, StorageDiffFilter

ETH_DECIMALS = 18

_DEN = Decimal(10**ETH_DECIMALS)

GRPC_CONFIG = json.dumps(
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

DATA_PATH_L2 = (Path(__file__).parent / 'starknetid_l2.json').resolve()
DATA_PATH_L1 = (Path(__file__).parent / 'starknetid_l1.json').resolve()

l2data = []
if DATA_PATH_L2.exists():
    with open(DATA_PATH_L2, 'r') as fin:
        l2data = json.load(fin)
START = max([row.get('block') for row in l2data]) + 1 if l2data else 10_554
print(START)


data = []
if DATA_PATH_L1.exists():
    with open(DATA_PATH_L1, 'r') as fin:
        data = json.load(fin)
unique_nodes = list(set(tx.get('sender')
                    for tx in data).union(tx.get('recipient') for tx in data))


def to_decimal(amount: int) -> Decimal:
    return Decimal(amount) / _DEN


async def main():

    briqs_address = felt.from_hex(
        "0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672"
    )

    ether_address = felt.from_hex(
        "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    )

    usdc_address = felt.from_hex(
        "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
    )

    usdt_address = felt.from_hex(
        "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
    )

    dai_address = felt.from_hex(
        "0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3",
    )

    wbtc_address = felt.from_hex(
        "0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac",
    )

    transfer_key = felt.from_hex(
        "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )

    table = {
        felt.to_hex(briqs_address): 'BRIQ',
        felt.to_hex(ether_address): 'ETH',
        felt.to_hex(usdc_address): 'USDC',
        felt.to_hex(usdt_address): 'USDT',
        felt.to_hex(dai_address): 'DAI',
        felt.to_hex(wbtc_address): 'WBTC',
    }

    channel = secure_channel("mainnet.starknet.a5a.ch",
                             ssl_channel_credentials(),
                             options=[
                                 ('grpc.max_receive_message_length', 128 * 1048576),
                                 ("grpc.service_config", GRPC_CONFIG)])

    (client, stream) = StreamService(channel).stream_data()

    filter = (
        Filter()
        .with_header(weak=False)
        .add_event(EventFilter().with_from_address(ether_address).with_keys([transfer_key]))
        # .add_event(EventFilter().with_from_address(usdc_address).with_keys([transfer_key]))
        # .add_event(EventFilter().with_from_address(usdt_address).with_keys([transfer_key]))
        # .add_event(EventFilter().with_from_address(dai_address).with_keys([transfer_key]))
        # .add_event(EventFilter().with_from_address(wbtc_address).with_keys([transfer_key]))
        .encode()
    )

    await client.configure(
        filter=filter,
        finality=DataFinality.DATA_STATUS_PENDING,
        batch_size=10,
        cursor=starknet_cursor(START)
    )

    block = Block()
    async for message in stream:
        if message.data is not None:

            new = list()
            for batch in message.data.data:
                block.ParseFromString(batch)

                block_number = block.header.block_number
                print(block_number)

                if block_number > 19_500:
                    sys.exit(1)

                for event_with_tx in block.events:
                    event = event_with_tx.event

                    sender = felt.to_hex(event.data[0])
                    recipient = felt.to_hex(event.data[1])

                    if (sender not in unique_nodes and recipient not in unique_nodes) or (int(sender, 16) * int(recipient, 16) == 0):
                        continue

                    tx = event_with_tx.transaction

                    time = block.header.timestamp.ToSeconds()
                    tx_hash = felt.to_hex(tx.meta.hash)
                    contract = felt.to_hex(event.from_address)
                    contract_name = table.get(contract)

                    value = felt.to_int(event.data[2]) + (
                        felt.to_int(event.data[3]) << 128
                    )

                    new.append({
                        'contract': contract,
                        'name': contract_name,
                        'time': time,
                        'block': block_number,
                        'hash': tx_hash,
                        'sender': sender,
                        'recipient': recipient,
                        'value': str(value),
                    })

            data = []
            if DATA_PATH_L2.exists():
                with open(DATA_PATH_L2, 'r') as fin:
                    data = json.load(fin)
            with open(DATA_PATH_L2, 'w') as fout:
                data.extend(new)
                json.dump(data, fout, indent=2)


if __name__ == "__main__":
    for i in range(20):
        try:
            asyncio.run(main())
        except Exception:
            time.sleep(10)
