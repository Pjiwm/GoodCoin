from globals import manager
from cli.Utils import *
from tabulate import tabulate
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from InquirerPy import inquirer


def show_blocks():

    index = 0
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    while True:
        clear_screen()

        block = manager.get_block(index)
        transactions = block.data
        data = []
        tx_num = 1
        for transaction in transactions:
            data.append((f"TX #{tx_num}", "-----"))
            data.append(("User📦", "Value 💰"))
            for input in transaction.inputs:
                record = swapped_dict[input[0]], -input[1]
                data.append(record)
            for output in transaction.outputs:
                record = swapped_dict[output[0]], output[1]
                data.append(record)
            data.append(("TRANSACTION FEE", transaction.calc_tx_fee()))
            data.append(("Validate transaction", transaction.is_valid()))
        if block.previousBlock:
            data.append(("Mining Reward ⛏️", "-----"))
            miner_name = swapped_dict[block.miner]
            data.append((miner_name, block.get_mining_reward()))
            data.append(("Block Data 📜", "-----"))
            data.append(("Nonce", block.nonce))
            data.append(("Hash", block.computeHash().hex()))
            data.append(("Previous Hash", block.previousHash.hex()))
            data.append(("Valid block", block.is_valid()))
            data.append((
                "Validation flags", f"Valid: {block.count_valid_flags()} Invalid: {block.count_valid_flags()}"))
        else:
            data.append(("Hash", block.computeHash().hex()))
            data.append(("Nonce", block.nonce))
            data.append(("Genesis Block", True))
        table = tabulate(
            data, headers=["Block 🧱", f"ID: {block.id}"], tablefmt="fancy_grid")
        print(table)
        print(f"Block #{block.id}")

        table_options = ["Previous Block", "Next Block", "Back"]
        option = inquirer.select(
            "Blockchain ⛓️", choices=table_options).execute()
        if option == table_options[0]:
            index += 1
        elif option == table_options[1]:
            index -= 1
        else:
            return ""

        if index >= block.id or index < 0:
            index = 0
