from gzip import READ
from operator import truediv
from optparse import AmbiguousOptionError
from core.Signature import *
from core.TxType import TxType
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import List, Union, NewType
from datetime import datetime

TxSelf = NewType('TxSelf', 'Tx')

class Tx:
    def __init__(self, type=TxType.Normal, uuid=None):
        self.type = type
        self.inputs: List[Tuple[bytes, int]] = []  # pub key, amount
        self.outputs: List[Tuple[bytes, int]] = []  # pub key, amount
        self.sigs: List[bytes] = []
        self.reqd: List[bytes] = []
        self.invalidations = []
        self.uuid_sign: Tuple[bytes, bytes] = None # signature, pubk
        self.uuid: bytes = uuid
        if type == TxType.Normal:
            self.__set_uuid()

    def __lt__(self, other):
        # Always puts reward tx first
        if self.type == TxType.Reward:
            return True
        if other.type == TxType.Reward:
            return False

        return -self.calc_tx_fee() < -other.calc_tx_fee()

    def __eq__(self, other: TxSelf):
        if not isinstance(other, Tx):
            return False
        if self.type != other.type:
            return False
        if self.type == TxType.Reward:
            return other.uuid == self.uuid

        if not self.uuid_sign:
            print("X")
            return False

        pub_k = pubk_from_bytes(self.uuid_sign[1])
        if verify(self.uuid, self.uuid_sign[0], pub_k) and verify(other.uuid, other.uuid_sign[0], pub_k):
            return self.uuid.hex() == other.uuid.hex()
        return False


    def add_input(self, from_addr: RSAPublicKey, amount: int):
        self.inputs.append((from_addr.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo), amount))

    def add_output(self, to_addr: Union[RSAPublicKey, bytes], amount):
        if isinstance(to_addr, bytes):
            self.outputs.append((to_addr, amount))
            return
        try:
            self.outputs.append((to_addr.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo), amount))
        except:
            self.outputs.append((None, amount))

    def add_reqd(self, addr: RSAPublicKey):
        self.reqd.append(addr.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

    def sign(self, private: RSAPrivateKey):
        message = self.__gather()
        newsig = sign(message, private)
        self.sigs.append(newsig)
        if self.type == TxType.Normal:
            self.__update_uuid(private)

    def is_tx_author(self, addr: RSAPublicKey):
        pubk = addr.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        return pubk in [addr for addr, _ in self.inputs]

    def is_valid(self):
        self.invalidations = []
        if self.type == TxType.Reward:
            return self.is_reward_valid()
        else:
            return self.is_regular_transaction_valid()

    def is_reward_valid(self):
        if len(self.inputs) == 0 and len(self.outputs) == 1:
            return True
        self.invalidations.append(
            "Reward transaction must have exactly one output.")
        return False

    def is_regular_transaction_valid(self):
        if self.has_negative_amount():
            self.invalidations.append("Amount cannot be negative.")
            return False

        output_keys = all(item is not None for item, _ in self.outputs)
        if not output_keys:
            self.invalidations.append("Output or output key is invalid.")
            return False

        total_in = sum(amount for _, amount in self.inputs)
        total_out = sum(amount for _, amount in self.outputs)

        if total_out > total_in:
            self.invalidations.append(
                "Total output is greater than total input.")
            return False

        if not all(self.is_input_valid(addr) for addr, _ in self.inputs):
            self.invalidations.append("Input signature is invalid.")
            return False

        if not all(self.is_required_signature_valid(addr) for addr in self.reqd):
            self.invalidations.append("Required signature is invalid.")
            return False

        return True

    def is_input_valid(self, addr):
        for s in self.sigs:
            if verify(self.__gather(), s, pubk_from_bytes(addr)):
                return True
        return False

    def has_negative_amount(self):
        if any(amount < 0 for _, amount in self.inputs):
            return True
        if any(amount < 0 for _, amount in self.outputs):
            return True
        return False

    def is_required_signature_valid(self, addr):
        for s in self.sigs:
            if verify(self.__gather(), s, pubk_from_bytes(addr)):
                return True
        return False

    def __update_uuid(self, priv_key: RSAPrivateKey):
        signature =  sign(self.uuid, priv_key)
        pub_k = priv_key.public_key()
        pub_k_bytes = pub_k.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        self.uuid_sign = (signature, pub_k_bytes)


    def __set_uuid(self):
        current_time = datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(time_string), 'utf8'))
        self.uuid = digest.finalize()

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
            repr_str = repr_str + str(addr) + "\n"

        repr_str += "SIGNATURES:\n"
        for sig in self.sigs:
            repr_str = repr_str + str(sig) + "\n"

        repr_str += "END\n"

        return repr_str

    def __bytes__(self):
        return str(self).encode("utf-8")

    def calc_tx_fee(self):
        total_in = sum(amount for _, amount in self.inputs)
        total_out = sum(amount for _, amount in self.outputs)
        return max(0, total_in - total_out)
