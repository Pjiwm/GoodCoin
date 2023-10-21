from gzip import READ
from operator import truediv
from optparse import AmbiguousOptionError
from core.Signature import *
from core.TxType import TxType
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from typing import List


class Tx:
    def __init__(self, type=TxType.Normal):
        self.type = type
        self.inputs: List[Tuple[RSAPublicKey, int]] = []
        self.outputs: List[Tuple[RSAPublicKey, int]] = []
        self.sigs: List[bytes] = []
        self.reqd: List[RSAPublicKey] = []

    def add_input(self, from_addr: RSAPublicKey, amount: int):
        self.inputs.append((from_addr, amount))

    def add_output(self, to_addr, amount):
        self.outputs.append((to_addr, amount))

    def add_reqd(self, addr):
        self.reqd.append(addr)

    def sign(self, private: RSAPrivateKey):
        message = self.__gather()
        newsig = sign(message, private)
        self.sigs.append(newsig)

    def is_valid(self):
        if self.type == TxType.Reward:
            return self.is_reward_valid()
        else:
            return self.is_regular_transaction_valid()

    def is_reward_valid(self):
        if len(self.inputs) == 0 and len(self.outputs) == 1:
            return True
        return False

    def is_regular_transaction_valid(self):
        total_in = sum(amount for _, amount in self.inputs)
        total_out = sum(amount for _, amount in self.outputs)

        if total_out > total_in:
            return False

        if not all(self.is_input_valid(addr) for addr, _ in self.inputs):
            return False

        if not all(self.is_required_signature_valid(addr) for addr in self.reqd):
            return False

        return True

    def is_input_valid(self, addr):
        for s in self.sigs:
            if verify(self.__gather(), s, addr):
                return True
        return False

    def is_required_signature_valid(self, addr):
        for s in self.sigs:
            if verify(self.__gather(), s, addr):
                return True
        return False

    def __gather(self):
        data = []
        data.append(self.inputs)
        data.append(self.outputs)
        data.append(self.reqd)
        return data

    def __repr__(self):

        repr_str = "INPUTS:\n"
        for addr, amt in self.inputs:
            repr_str = repr_str + str(amt) + "from" + str(addr) + "\n"

        repr_str += "OUTPUTS:\n"
        for addr, amt in self.outputs:
            repr_str = repr_str + str(amt) + "to" + str(addr) + "\n"

        repr_str += "EXTRA REQUIRED SIGNATURES:\n"
        for req_sig in self.reqd:
            repr_str = repr_str + str(req_sig) + "\n"

        repr_str += "SIGNATURES:\n"
        for sig in self.sigs:
            repr_str = repr_str + str(sig) + "\n"

        repr_str += "END\n"

        return repr_str

    def calc_tx_fee(self):
        if self.type == TxType.Reward:
            total_in = sum(amount for _, amount in self.inputs)
            total_out = sum(amount for _, amount in self.outputs)
            return max(0, total_in - total_out)
        return 0


class TxBuilder:
    def __init__(self, tx_type=TxType.Normal):
        self.tx = Tx(tx_type)

    def add_input(self, from_addr: RSAPublicKey, amount: int):
        self.tx.inputs.append((from_addr, amount))
        return self

    def add_output(self, to_addr: RSAPublicKey, amount: int):
        self.tx.outputs.append((to_addr, amount))
        return self

    def add_reqd(self, addr: RSAPublicKey):
        self.tx.reqd.append(addr)
        return self

    def sign(self, private_key: RSAPrivateKey):
        message = self.tx.__gather()
        newsig = sign(message, private_key)
        self.tx.sigs.append(newsig)
        return self

    def build(self):
        return self.tx
