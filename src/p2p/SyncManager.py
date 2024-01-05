from p2p.Client import Client
from p2p.Server import Server
from p2p.Requests import Request, RequestData
from p2p.Response import Response, TxResponse, AdressBookResponse, BlockResponse
from core.TxBlock import TxBlock
# from core.BlockchainManager import BlockchainManager
from typing import List

class SyncManager:
    def __init__(self, is_new: bool, blockchain: TxBlock) -> None:
        # self.manager = BlockchainManager
        self.client = Client()
        self.blockchain = blockchain
        self.blocks_ready = True
        self.blocks_done = False
        self.wipe_pool = False
        self.done_syncing = False

        self.new_blocks: TxBlock = None
        self.last_retrieved_block: TxBlock = None
        if not self.blockchain.previous_block and not is_new:
            self.blockchain = None
            # manager.store_block()
            print("Creating new blockchain environment...")
        if is_new:
            self.done_syncing = True

    def retrieve_data(self):
        response_result = 0
        tries = 0
        if not self.blocks_done:
                if self.blocks_ready:
                    print("Sending")
                    response_result = self.request_block()
                if response_result == 1:
                    print("No response....")
                    import os
                    tries += 1
                    if tries > 4:
                        os._exit(0)
                    self.blocks_ready = True


    def request_block(self):
        request_hash = self.last_retrieved_block.previous_hash if self.last_retrieved_block else None
        req = RequestData(Request.GetBlock, request_hash)
        print("Requesting block", request_hash)
        result = self.client.send_request(req)
        self.blocks_ready = False
        print(result)
        return result

    def accept_response(self, data: List[Response]):
        print(data)
        for response in data:
            if isinstance(response, BlockResponse):
                self.accept_block(response)

    def accept_block(self, response: BlockResponse):
        new_block = response.block
        self.last_retrieved_block = new_block

        if not self.new_blocks:
            self.new_blocks = new_block
            self.block_progress()
            return

        curr = self.new_blocks
        while curr.previous_block:
            curr = curr.previous_block
        curr.previous_block = new_block
        self.block_progress()

    def block_progress(self):
        pass
        # done_from_start = not self.blockchain and self.last_retrieved_block.previous_hash == None
        # retrieved_all_new = self.blockchain.computeHash() == self.last_retrieved_block.previous_hash
        # self.blocks_done = done_from_start or retrieved_all_new
