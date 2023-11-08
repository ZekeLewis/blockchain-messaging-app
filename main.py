#main.py
import argparse
from user import run_node
import random


def main():
    parser = argparse.ArgumentParser(description="Blockchain Node")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the node")
    parser.add_argument("--nodes", type=int, default=1, help="Number of nodes to run")
    parser.add_argument("--user", type=str, default='Joe', help="String username")
    args = parser.parse_args()

    for i in range(args.nodes):
        port = args.port + i
        user_id = hash(args.user)
        run_node(port, user_id)

if __name__ == '__main__':
    main()
