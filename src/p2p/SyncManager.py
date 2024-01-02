from globals import manager
from p2p.Client import Client
from p2p.Server import Server
import time
from p2p.Requests import Request, RequestData
from core.TxBlock import TxBlock

class SyncManager:
    def __init__(self, is_new: bool) -> None:
        self.client = Client()
        self.server = Server()
        self.done = False
        self.wipe_pool = False

        self.new_blocks: TxBlock = None
        self.last_retrieved_block: TxBlock = None
        if not manager.block.previous_block and not is_new:
            manager.block = None
            manager.store_block()
            print("Creating new blockchain environment...")



    def retrieve_data(self):
        self.request_block()


    def request_block(self):
        req = RequestData(Request.GetBlock, self.last_retrieved_block.previous_hash)
        manager.client.send_request(req)
        time.sleep(0.1)