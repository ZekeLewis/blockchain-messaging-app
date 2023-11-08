# storage.py

import json
from blockchain_2.block_chain import Chain, Block

CHAINDATA_DIR = 'chaindata/'

def save_chain_to_file(chain):
    # Save the blockchain data to a file
    data = [block.to_dict() for block in chain.blocks]
    with open('blockchain.json', 'w') as blockchain_file:
        json.dump(data, blockchain_file)

def load_chain_from_file():
    # Load the blockchain data from a file
    try:
        with open('blockchain.json', 'r') as blockchain_file:
            data = json.load(blockchain_file)
        blocks = [Block.from_dict(block_data) for block_data in data]
        return Chain(blocks)
    except FileNotFoundError:
        return Chain([])
