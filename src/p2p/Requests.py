from enum import Enum
from typing import Optional, Union
import os

class Request(Enum):
    GetBlock = 1
    GetTransactions = 2
    GetAddressBook = 3

class RequestData:
    def __init__(self, request_type: Request, data: Optional[Union[bytes, None]] = None):
        self.request_type = request_type
        self.data = data
        # client = "goodcoin_python" if os.environ.get('CLIENT') == 1 else "goodcoin_client2"
        client = os.environ.get('CLIENT')
        if client == "1":
            self.recipient = "python_goodcoin"
        else:
            self.recipient = "client2_goodcoin"