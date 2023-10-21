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
from typing import Tuple

USER_PATH = "data/users/"


def generate_keys() -> Tuple[RSAPrivateKey, RSAPublicKey]:
    private_key = generate_private_key(
        public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

# TODO 1: Sign a passed message using a given private key
# Make sure the message is encoded correctly before signing
# Signing and verifying algorithms must be the same


def sign(message: bytes, private_key: RSAPrivateKey) -> bytes:
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def verify(message: bytes, signature: bytes, public_key: RSAPublicKey) -> bool:
    try:
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


def save_keys(keys_file_name: str, keys: Tuple[RSAPrivateKey, RSAPublicKey], pw: str):
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


def load_keys(keys_file_name: str, pw: str) -> Tuple[RSAPrivateKey, RSAPublicKey]:
    file = open(USER_PATH + keys_file_name, 'rb')
    key_set = pickle.load(file)
    file.close()
    return (serialization.load_pem_private_key(
        key_set[0], str.encode(pw), default_backend()),
        serialization.load_pem_public_key(key_set[1], default_backend()))

def username_available(name: str) -> bool:
    file_path = os.path.join(USER_PATH, name + ".pem")
    return not os.path.isfile(file_path)