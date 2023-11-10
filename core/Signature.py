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
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from typing import Tuple, Dict

USER_PATH = "data/users/"
USER_DB = "data/users.dat"
def create_data_folder_and_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(USER_DB):
        with open(USER_DB, 'xb'):
            pass

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


def save_user_keys(user_name: str, keys: Tuple[RSAPrivateKey, RSAPublicKey], pw: str):
    file = open(USER_DB, 'rb+')
    try:
        db = pickle.load(file)
    except:
        db = {}
    file.close()
    priv = keys[0].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(
            str.encode(pw))
    )
    file = open(USER_DB, 'wb')
    pub = keys[1].public_bytes(encoding=serialization.Encoding.PEM,
                               format=serialization.PublicFormat.SubjectPublicKeyInfo
                               )
    db[user_name] = (priv, pub)
    pickle.dump(db, file, -1)
    file.close()


def load_user_keys(username: str, pw: str) -> Tuple[RSAPrivateKey, RSAPublicKey]:
    file = open(USER_DB, 'rb')
    db = pickle.load(file)
    if not db[username]:
        raise ValueError("User not found.")
    key_set = db[username]
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
    file = open(USER_DB, 'wb')
    pickle.dump(loaded_address_book, file, -1)
    file.close()


def pubk_from_bytes(addr: bytes):
    return load_pem_public_key(addr, backend=default_backend())

def load_address_book() -> Dict[str, RSAPublicKey]:
    try:
        file = open(USER_DB, 'rb')
        db = pickle.load(file)
        file.close()
        public_key_dict = {key: serialization.load_pem_public_key(
                public_key, default_backend()) for key, (_, public_key) in db.items()}
        return public_key_dict
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
    file = open(USER_DB, 'rb+')
    try:
        db = pickle.load(file)
    except:
        file.close()
        return True
    file.close()
    return not db.get(name)
