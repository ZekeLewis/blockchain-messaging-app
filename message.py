import binascii
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils, padding
from cryptography.exceptions import InvalidSignature

class Message:
    def __init__(self, sender_public_key, recipient_public_key, content):
        self.sender_public_key = sender_public_key
        self.recipient_public_key = recipient_public_key
        self.content = content
        self.signature = None

    def sign_message(self, private_key):
        # Sign the message with the sender's private key
        signature = private_key.sign(
            self.content.encode('utf-8'),
            padding.PKCS1v15(),
            utils.hashes.SHA256()
        )
        self.signature = binascii.hexlify(signature).decode()

    def verify_message(self):
        # Verify the signature of the message using the sender's public key
        sender_public_key = serialization.load_pem_public_key(
            self.sender_public_key.encode(),
        )
        signature = bytes.fromhex(self.signature)
        content = self.content.encode('utf-8')
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
