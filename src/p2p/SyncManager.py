from p2p.Client import Client
from p2p.Server import Server
from p2p.Requests import Request, RequestData
from p2p.Response import Response, TxResponse, AdressBookResponse, BlockResponse
from core.TxBlock import TxBlock
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing import List, Dict
import os


class SyncManager:
    def __init__(self, is_new: bool, blockchain: TxBlock) -> None:
        if not blockchain.previous_block:
            blockchain = None

        self.client = Client()
        self.blockchain = blockchain
        self.contains_genesis = False
        self.blocks_ready = True
        self.blocks_done = False
        self.wipe_pool = False
        self.done_syncing = False
        self.should_sync = not is_new

        self.users_done = False
        self.address_book: Dict[str, RSAPublicKey] = {}

        self.transactions_done = False
        self.transactions = []

        self.tries = 0

        self.new_blocks: TxBlock = None
        self.last_retrieved_block: TxBlock = None
        if not self.blockchain:
            print("Creating new blockchain environment...")
        if not self.should_sync:
            self.done_syncing = True

    def retrieve_data(self):
        if self.done_syncing:
            return

        # Users
        users_result = 0
        if not self.users_done:
            users_result = self.request_users()
            if users_result != 0:
                self.tries += 1
                if self.tries > 4:
                    print("Could not contact any nodes. Exiting...")
                    os._exit(0)
            else:
                self.users_done = True
                self.tries = 0
                print("Users retrieved")

        # Transactions
        transactions_result = 0
        if not self.transactions_done:
            transactions_result = self.request_transactions()
            if transactions_result != 0:
                self.tries += 1
                if self.tries > 4:
                    print("Could not contact any nodes. Exiting...")
                    os._exit(0)
            else:
                self.transactions_done = True
                self.tries = 0
                print("Transactions retrieved")

        # Blocks
        block_result = 0
        if not self.blocks_done:
                if self.blocks_ready:
                    block_result = self.request_block()
                if block_result != 0:
                    print("No response....")
                    self.tries += 1
                    if self.tries > 4:
                        print("Could not contact any nodes. Exiting...")
                        os._exit(0)
                    self.blocks_ready = True

        self.done_syncing = self.blocks_done and self.users_done


    def request_block(self):
        request_hash = self.last_retrieved_block.previous_hash if self.last_retrieved_block else None
        req = RequestData(Request.GetBlock, request_hash)
        hash_str = request_hash.hex() if request_hash else "LATEST BLOCK"
        print("Requesting block", hash_str)
        result = self.client.send_request(req)
        self.blocks_ready = False
        return result

    def request_users(self):
        req = RequestData(Request.GetAddressBook, None)
        result = self.client.send_request(req)
        print("Requesting users")
        return result

    def request_transactions(self):
        req = RequestData(Request.GetTransactions, None)
        result = self.client.send_request(req)
        print("Requesting transactions")
        return result

    def accept_response(self, data: List[Response]):
        for response in data:
            if isinstance(response, BlockResponse):
                self.accept_block(response)
            elif isinstance(response, AdressBookResponse):
                self.accept_users(response)
            elif isinstance(response, TxResponse):
                self.accept_transactions(response)

    def accept_users(self, response: AdressBookResponse):
        self.address_book = response.get_dictionary()
        print("Accepted users")


    def accept_transactions(self, response: TxResponse):
        self.transactions = response.transactions
        print("Accepted transactions")


    def accept_block(self, response: BlockResponse):
        accepted_block = response.block
        self.last_retrieved_block = accepted_block
        self.blocks_ready = True
        print("Accepted block", accepted_block.computeHash().hex())

        if not self.new_blocks:
            self.new_blocks = accepted_block
            self.block_progress()
            return

        curr = self.new_blocks
        curr = self.new_blocks
        while curr.previous_block:
            curr = curr.previous_block
        curr.previous_block = accepted_block
        self.block_progress()
        return

    def block_progress(self):
        if self.last_retrieved_block.previous_hash == None:
            self.blocks_done = True
            self.contains_genesis = True
            print("Done syncing blocks until genesis")
            return

        elif not self.blockchain:
            return

        elif self.blockchain.computeHash() == self.last_retrieved_block.previous_hash:
            print("Done syncing blocks")
            self.blocks_done = True
            return
