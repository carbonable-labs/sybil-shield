import json
from pathlib import Path

path = Path('./starknetid.json')
output = path.parent / 'result.json'

with open(path, 'r') as fin:
    data = json.load(fin)

nodes = data.get('nodes')
links = data.get('links')

targets, sources = zip(*[(link.get('target'), link.get('source')) for link in links])
link_nodes = targets + sources
unique_link_nodes = set(link_nodes)
print(len(unique_link_nodes))

removes = [node for node in unique_link_nodes if link_nodes.count(node) > 1]
removes = [node for node in unique_link_nodes if link_nodes.count(node) > 1]
print(len(removes))