# config.py

# Main settings
PORT = 5000  # Default port for the blockchain node
NUM_NODES = 4  # Number of nodes to run

# Blockchain settings
CHAINDATA_DIR = 'chaindata/'  # Directory for storing blockchain data
NUM_ZEROS = 6  # Number of leading zeros in the proof of work
STANDARD_ROUNDS = 100000  # Number of rounds for mining
PEERS = [
    'http://localhost:5000/',
    'http://localhost:5001/',
    'http://localhost:5002/',
    'http://localhost:5003/',
]

# Cryptography settings
RSA_KEY_SIZE = 2048  # RSA key size for user key pairs

# Scheduler settings
MINING_JOB_ID = 'mining'  # Job ID for the mining job

# P2P settings
PEER_NODES = [f'http://localhost:{PORT + i}/' for i in range(NUM_NODES)]

# Message settings
SIGNATURE_ALGORITHM = 'RSASSA-PSS'  # Signature algorithm for message signing
SIGNATURE_HASH_ALGORITHM = 'SHA256'  # Hash algorithm for message signing

# User settings
USER_DATA_DIR = 'user_data/'  # Directory for storing user data
