# block_chain.py
import hashlib
import time
import json
import binascii
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from config import *

class Block:
    def __init__(self, index, prev_hash, data, timestamp, nonce, hash=None):
        self.index = index
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = hash or self.update_self_hash()
        self.encrypted_messages = []

    def header_string(self):
        return str(self.index) + self.prev_hash + self.data + str(self.timestamp) + str(self.nonce)

    @classmethod
    def from_dict(cls, block_dict):
        return cls(
            block_dict['index'],
            block_dict['prev_hash'],
            block_dict['data'],
            block_dict['timestamp'],
            block_dict['nonce'],
            block_dict['hash']
        )

    def update_self_hash(self):
        sha = hashlib.sha256()
        sha.update(self.header_string().encode())
        new_hash = sha.hexdigest()
        self.hash = new_hash
        return new_hash

    def self_save(self):
        index_string = str(self.index).zfill(6)
        filename = f'{CHAINDATA_DIR}{index_string}.json'
        with open(filename, 'w') as block_file:
            json.dump(self.to_dict(), block_file)

    def add_encrypted_message(self, sender_address, recipient_address, content, signature, timestamp):
        self.encrypted_messages.append({
            "sender_address": sender_address,
            "recipient_address": recipient_address,
            "content": content,
            "signature": signature,
            "timestamp": timestamp
        })

    def validate_encrypted_messages(self, public_keys):
        for message in self.encrypted_messages:
            sender_key = public_keys.get(message['sender_address'])
            if not sender_key:
                return False
            signature = binascii.unhexlify(message['signature'])
            content = message['content'].encode('utf-8')
            try:
                sender_key.verify(
                    signature,
                    content,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            except InvalidSignature:
                return False
        return True
    

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "encrypted_messages": self.encrypted_messages
        }

    def is_valid(self):
        self.update_self_hash()
        if str(self.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            return True
        return False

class Chain:
    def __init__(self, blocks):
        self.blocks = blocks

    def is_valid(self):
        for index, cur_block in enumerate(self.blocks[1:], start=1):
            prev_block = self.blocks[index - 1]
            if not cur_block.is_valid() or cur_block.prev_hash != prev_block.hash:
                return False
        return True

    def self_save(self):
        with open('blockchain.json', 'w') as blockchain_file:
            json.dump(self.block_list_dict(), blockchain_file)

    def find_block_by_index(self, index):
        for block in self.blocks:
            if block.index == index:
                return block
        return None

    def find_block_by_hash(self, hash):
        for block in self.blocks:
            if block.hash == hash:
                return block
        return None

    def most_recent_block(self):
        if self.blocks:
            return self.blocks[-1]
        return None

    def max_index(self):
        if self.blocks:
            return self.blocks[-1].index
        return -1

    def add_block(self, new_block):
        if new_block.index == self.max_index() + 1 and new_block.is_valid():
            self.blocks.append(new_block)
            self.self_save()
            return True
        return False

    def block_list_dict(self):
        return [block.to_dict() for block in self.blocks]




def create_new_block_from_prev(prev_block=None, data=None):
    if prev_block is None:
        index = 0
        prev_hash = "0"
        timestamp = int(time.time())
    else:
        index = prev_block.index + 1
        prev_hash = prev_block.hash
        timestamp = int(time.time())
    nonce = 0
    new_block = Block(index, prev_hash, data, timestamp, nonce)
    return new_block

def sync_local():
    #synchronize the local blockchain with peers
    local_chain = Chain([])
    for peer in PEERS:
        try:
            response = requests.get(peer + 'blockchain.json')
            peer_chain_data = response.json()
            blocks = [Block.from_dict(block_data) for block_data in peer_chain_data]
            if len(blocks) > len(local_chain.blocks):
                local_chain.blocks = blocks
        except requests.exceptions.RequestException:
            pass
    return local_chain

def broadcast_mined_block(new_block):
    block_info_dict = new_block.to_dict()
    for peer in PEERS:
        try:
            requests.post(peer + 'mined', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            pass
    return True

def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    new_block = create_new_block_from_prev(prev_block, timestamp=timestamp)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)

def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    for nonce in range(start_nonce, start_nonce + rounds):
        new_block.nonce = nonce
        new_block.update_self_hash()
        if str(new_block.hash[:NUM_ZEROS]) == '0' * NUM_ZEROS:
            new_block.self_save()
            broadcast_mined_block(new_block)
            return new_block, rounds, start_nonce, new_block.timestamp
    return None, rounds, start_nonce, new_block.timestamp


