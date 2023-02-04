from app.models import AbstractModel


class BaseModel(AbstractModel):

    def __init__(self, layer1, layer2):
        super().__init__(layer1, layer2)

    def run(self, _):
        # Suspect nodes
        senders = set(node.get('sender') for node in self._layer1)
        recipients = set(node.get('recipient')
                         for node in self._layer1 if int(node.get('sender'), 16) == 0)
        suspects = list(senders.union(recipients))
        print(f"Suspects: {len(suspects)}")

        # Score
        txs = self._layer1 + self._layer2
        total_txs = [len([tx for tx in txs if tx['sender'] == suspect])
                     for suspect in suspects]
        print(f"Total txs: {len(total_txs)}")
        internal_txs = [len([
            tx for tx in txs
            if (tx['sender'] == suspect and tx['recipient'] in suspects)
            # or (tx['recipient'] == suspect and tx['sender'] in suspects)
        ]) for suspect in suspects]
        print(f"Internal txs: {len(internal_txs)}")
        scores = [num / den if den else 0 for num,
                  den in zip(internal_txs, total_txs)]
        print(f"Scores: {len(scores)}")

        # Nodes
        nodes = [
            {'id': address, 'name': address, 'val': 1, 'score': score}
            if int(address, 16) != 0 else
            {'id': address, 'name': address, 'val': 5, 'score': 0}
            # if address in layer1_nodes else
            # {'id': address, 'name': address, 'val': 0}
            for address, score in zip(suspects, scores)
        ]
        print(f"Nodes: {len(nodes)}")

        # Links
        links = [
            {'source': tx.get('sender'), 'target': tx.get('recipient')}
            for tx in self._layer1 + self._layer2  # BRIQ and ETH txs
            # for tx in  self._layer2  # ETH txs
            if tx.get('sender') in suspects
            and tx.get('recipient') in suspects
        ]
        print(f"Links: {len(links)}")
        unique_links = list({
            int(link['source'], 16) + int(link['target'], 16): link
            for link in links
        }.values())

        return {'nodes': nodes, 'links': unique_links}
