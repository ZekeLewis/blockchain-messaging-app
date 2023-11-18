# p2p.py
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from block_chain import Chain, Block, create_new_block_from_prev
from config import *


def sync_local():
    local_chain = Chain([])
    for peer in PEERS:
        try:
            response = requests.get(peer + 'blockchain.json')
            peer_chain_data = response.json()
            blocks = [Block.from_dict(block_data) for block_data in peer_chain_data]
            if len(blocks) > len(local_chain):
                local_chain = Chain(blocks)
        except requests.exceptions.RequestException:
            pass
    return local_chain

def sync(save=False):
    local_chain = sync_local()
    if save:
        local_chain.self_save()
    return local_chain

def broadcast_mined_block(new_block):
    block_info_dict = new_block.to_dict()
    for peer in PEERS:
        try:
            requests.post(peer + 'mined', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            pass
    return True

def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    if chain is None:
        chain = sync_local()
    prev_block = chain.most_recent_block()
    return mine_from_prev_block(prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp)

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

sched = BackgroundScheduler()
sched.add_job(mine_for_block, kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')
sched.start()
