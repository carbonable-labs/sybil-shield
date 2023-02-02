import asyncio
from decimal import Decimal
import json

from grpc import ssl_channel_credentials
from grpc.aio import secure_channel

from apibara.protocol import StreamService
from apibara.protocol.proto.stream_pb2 import DataFinality
from apibara.starknet import Block, EventFilter, Filter, felt
from apibara.starknet.filter import StateUpdateFilter, StorageDiffFilter

ETH_DECIMALS = 18

_DEN = Decimal(10**ETH_DECIMALS)


def to_decimal(amount: int) -> Decimal:
    return Decimal(amount) / _DEN


async def main():
    address = felt.from_hex(
        "0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672"
    )

    # `Transfer` selector.
    # You can get this value either with starknet.py's `ContractFunction.get_selector`
    # or from starkscan.
    transfer_key = felt.from_hex(
        "0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"
    )

    channel = secure_channel("mainnet.starknet.a5a.ch",
                             ssl_channel_credentials())

    (client, stream) = StreamService(channel).stream_data()

    filter = (
        Filter()
        .with_header(weak=True)
        # .add_event(EventFilter().with_from_address(address))
        .encode()
    )

    await client.configure(
        filter=filter,
        finality=DataFinality.DATA_STATUS_FINALIZED,
        batch_size=10,
    )

    block = Block()
    data = dict()
    async for message in stream:
        if message.data is not None:
            for batch in message.data.data:
                block.ParseFromString(batch)

                print(
                    f"B {block.header.block_number} / {felt.to_hex(block.header.block_hash)}"
                )

                for event_with_tx in block.events:
                    event = event_with_tx.event
                    tx = event_with_tx.transaction

                    tx_hash = felt.to_hex(tx.meta.hash)

                    from_addr = felt.to_hex(event.data[0])
                    to_addr = felt.to_hex(event.data[1])
                    amount = felt.to_int(event.data[2]) + (
                        felt.to_int(event.data[3]) << 128
                    )
                    amount = to_decimal(amount)

                    print(f"T {from_addr} => {to_addr}")
                    print(f" Amount: {amount} ETH")
                    print(f"Tx Hash: {tx_hash}")
                    print()

                    data.setdefault(tx_hash, {
                        'block': int(block.header.block_number),
                        'from': str(from_addr),
                        'to': str(to_addr),
                        'amount': int(amount),
                    })

                    if block.header.block_number == 19418:
                        with open('briq.json', 'w') as fout:
                            print(data)
                            json.dump(data, fout)


if __name__ == "__main__":
    asyncio.run(main())
