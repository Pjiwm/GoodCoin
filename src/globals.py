from core.BlockchainManager import BlockchainManager
import argparse
import os

parser = argparse.ArgumentParser(description='The goodchain wallet.')
parser.add_argument('--new', type=bool, help='Specify if you want to create blockchain from scratch(true/false)')
args = parser.parse_args()

make_new = args.new if args.new else False

manager = BlockchainManager(make_new)