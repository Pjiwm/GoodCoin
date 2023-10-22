#!/usr/bin/env python3
"""Asymmetric Cryptography -> Digital Signature: Homework

The goal of this homework is to learn how to store and load asymmetric keys of different users on a disk.
In addition, to sign and verify messages using those keys. Furthermore, it is required to encrypt keys before saving using a password.
In this implementation the passed message as an argument is a string. Proper encoding and decoding is need before usage.
When signing a message the RSA sign-function requires a specific hash like SHA256, and padding such as PSS.
RSA verify function calculates the message hash. Decrypt the signature then compares both values to verify.
Be aware that verification must use the same algorithm values as signing to correctly verify the signature.

Your task is to:
    * locate the TODOs in this file
    * complete the missing part from the code
    * run the test of this tutorial located in same folder.

To test run 'Signature_t.py' in your command line

Notes:
    * do not change class structure or method signature to not break unit tests
    * visit this url for more information on this topic:
    https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/
"""

import os
import pickle
from cryptography.exceptions import *
from cryptography.hazmat.primitives.asymmetric.rsa import *
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Dict

USER_PATH = "data/users/"
ADDRES_BOOK_PATH = "data/address_book/users.keys"


def generate_keys() -> Tuple[RSAPrivateKey, RSAPublicKey]:
    private_key = generate_private_key(
        public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def sign(message, private_key: RSAPrivateKey) -> bytes:
    message = bytes(str(message), 'utf-8')
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def verify(message, signature: bytes, public_key: RSAPublicKey) -> bool:
    try:
        message = bytes(str(message), 'utf-8')
        public_key.verify(
            signature,
            message,
            padding.PSS(

                mgf=padding.MGF1(hashes.SHA256()),

                salt_length=padding.PSS.MAX_LENGTH

            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


def save_user_keys(keys_file_name: str, keys: Tuple[RSAPrivateKey, RSAPublicKey], pw: str):
    file = open(USER_PATH + keys_file_name, 'wb')
    priv = keys[0].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(
            str.encode(pw))
    )

    pub = keys[1].public_bytes(encoding=serialization.Encoding.PEM,
                               format=serialization.PublicFormat.SubjectPublicKeyInfo
                               )
    pickle.dump((priv, pub), file, -1)
    file.close()


def load_user_keys(keys_file_name: str, pw: str) -> Tuple[RSAPrivateKey, RSAPublicKey]:
    file = open(USER_PATH + keys_file_name, 'rb')
    key_set = pickle.load(file)
    file.close()
    return (serialization.load_pem_private_key(
        key_set[0], str.encode(pw), default_backend()),
        serialization.load_pem_public_key(key_set[1], default_backend()))


def store_in_address_book(username: str, public_key: RSAPublicKey):
    loaded_address_book = load_address_book()
    loaded_address_book = __map_key_dict(loaded_address_book)
    pub_bytes = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                                        )
    loaded_address_book[username] = pub_bytes
    file = open(ADDRES_BOOK_PATH, 'wb')
    pickle.dump(loaded_address_book, file, -1)
    file.close()


def load_address_book() -> Dict[str, RSAPublicKey]:
    try:
        file = open(ADDRES_BOOK_PATH, 'rb')
        file_load = pickle.load(file)
        file.close()
        address_book = {
            name: serialization.load_pem_public_key(
                key, default_backend())
            for (name, key) in file_load.items()
        }
        return address_book
    except:
        return {}


def __map_key_dict(dict: Dict[str, RSAPublicKey]) -> Dict[str, bytes]:
    return {
        name: key.public_bytes(encoding=serialization.Encoding.PEM,
                               format=serialization.PublicFormat.SubjectPublicKeyInfo
                               )
        for (name, key) in dict.items()
    }

def string_hash(message: str) -> str:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(bytes(message, 'utf8'))
    return digest.finalize().hex()


def username_available(name: str) -> bool:
    file_path = os.path.join(USER_PATH, name + ".pem")
    return not os.path.isfile(file_path)
