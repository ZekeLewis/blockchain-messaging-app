# user.py
import os
import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from message import Message
from config import *

class UserNode:
    def __init__(self, port, user_id):
        self.port = port
        self.user_id = user_id
        self.key_file = f"user_{user_id}_keys.pem"
        self.peers = []
        self.num_stars = 0 #user gets stars for mining blocks

        if os.path.exists(self.key_file):
            self.private_key, self.public_key = self.load_keys_from_file()
        else:
            self.private_key, self.public_key = self.generate_and_save_keys()

    def load_keys_from_file(self):
        with open(self.key_file, "rb") as key_file:
            key_data = key_file.read()
            private_key = serialization.load_pem_private_key(key_data, password=None)
            public_key = private_key.public_key()
        return private_key, public_key

    def generate_and_save_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        with open(self.key_file, "wb") as key_file:
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            key_file.write(key_data)

        return private_key, public_key

    def get_public_key_pem(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def create_message(self, recipient_public_key_pem, content):
        recipient_public_key = serialization.load_pem_public_key(
            recipient_public_key_pem.encode(),
        )
        message = Message(self.get_public_key_pem(), recipient_public_key_pem, content)
        message.sign_message(self.private_key)
        return message

    def verify_message(self, message):
        sender_public_key = serialization.load_pem_public_key(
            message.sender_public_key.encode(),
        )
        signature = bytes.fromhex(message.signature)
        content = message.content.encode('utf-8')
        try:
            sender_public_key.verify(
                signature,
                content,
                padding.PKCS1v15(),
                utils.hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        
    def award_star(self):
        self.num_stars += 1
        print(f"User {self.user_id} now has {self.num_stars} stars!")

    def connect_to_peers(self, peers):
        #this function is still incomplete
        #we need to configure some way to connect to other users
        for peer in peers:
            self.peers.append(peer)

        
def run_node(port, user_id, action):
    #had to keep this import here to prevent errors without refactoring the entire code
    from cli import interact_with_blockchain
    user_node = UserNode(port, user_id)
    user_node.connect_to_peers(PEERS) #needs to create a local instance from peers syncing the blockchain
    interact_with_blockchain(action, user_id, port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Blockchain Node")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the node")
    parser.add_argument("--nodes", type=int, default=1, help="Number of nodes to run")
    parser.add_argument("--user", type=str, default='Joe', help="String username")
    parser.add_argument("action", choices=["send", "receive"], help="Action to perform")
    args = parser.parse_args()

    for i in range(args.nodes):
        port = args.port + i
        user_id = hash(args.user)
        run_node(port, user_id, args.action)