#cli.py
import argparse
from block_chain import sync_local, mine_from_prev_block, broadcast_mined_block
from cryptography.hazmat.primitives import serialization
import time
import os

def load_sender_private_key(user_id):
    key_file = f"user_{user_id}_keys.pem"
    if not os.path.exists(key_file):
        print(f"Private key file {key_file} does not exist. Make sure it's generated.")
        return None
    with open(key_file, 'rb') as private_key_file:
        private_key_pem = private_key_file.read()
        return serialization.load_pem_private_key(private_key_pem, password=None)

def send_message(sender_private_key, recipient_address, content, timestamp):
    local_chain = sync_local()
    block = mine_from_prev_block(local_chain.most_recent_block())
    if not block:
        print("Failed to mine a block.")
        return

    block.add_encrypted_message(sender_private_key, recipient_address, content, timestamp)
    broadcast_mined_block(block)
    print("Message sent and added to the blockchain.")

def receive_messages(user_id):
    local_chain = sync_local()
    messages = []

    for block in local_chain.blocks:
        for message in block.encrypted_messages:
            if message['recipient_address'] == user_id:
                messages.append(message)

    for message in messages:
        print(f"Sender: {message['sender_address']}")
        print(f"Recipient: {message['recipient_address']}")
        print(f"Content: {message['content']}")
        print("-----")

def interact_with_blockchain(action, user_id, port):
    if action == "send":
        sender_private_key = load_sender_private_key(user_id)
        if sender_private_key is None:
            return
        recipient_address = input("Recipient Address: ")
        content = input("Message Content: ")
        timestamp = time.time()
        send_message(sender_private_key, recipient_address, content, timestamp)
    elif action == "receive":
        receive_messages(user_id)