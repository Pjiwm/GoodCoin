from enum import Enum
from typing import Optional, Union

class Request(Enum):
    GetBlock = 1
    GetTransactions = 2
    GetAddressBook = 3

class RequestData:
    def __init__(self, request_type: Request, data: Optional[Union[bytes, None]] = None):
        self.request_type = request_type
        self.data = data