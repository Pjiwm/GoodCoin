from globals import manager
from cli.Utils import *
from tabulate import tabulate
from core.TxType import *
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from InquirerPy import inquirer


def mine_block():
    clear_screen()
    print("Mining....")
    print(manager.mine_block())
    print("")
    inquirer.select("Return to main menu:", choices=["proceed"]).execute()


def show_blocks():

    index = 0
    max = manager.block.id
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    while True:
        clear_screen()

        block = manager.get_block(index)
        transactions = block.data
        tx_table = []
        block_table = []
        tx_num = 1
        for transaction in transactions:
            tx_table.append((f"TX #{tx_num}", "-----"))
            tx_table.append(("User📦", "Value 💰"))
            tx_num += 1
            for input in transaction.inputs:
                record = swapped_dict[input[0]], -input[1]
                tx_table.append(record)
            for output in transaction.outputs:
                record = swapped_dict[output[0]], output[1]
                tx_table.append(record)
            tx_table.append(("TRANSACTION FEE", transaction.calc_tx_fee()))
            tx_table.append(("Validate transaction", transaction.is_valid()))
        if block.previous_block:
            tx_table.append(("Mining Reward ⛏️", TxType.RewardValue.value))
            miner_name = swapped_dict[block.miner]
            tx_table.append((miner_name, block.get_mining_reward()))
            block_table.append(("Nonce", block.nonce))
            block_table.append(("Hash", block.block_hash.hex()))
            block_table.append(("Previous Hash", block.previous_hash.hex()))
            block_table.append(("Time of mining", block.time_of_creation))
            block_table.append(("Valid block", block.is_valid()))
            block_table.append((
                "Validation flags", f"Valid: {block.count_valid_flags()} Invalid: {block.count_valid_flags()}"))
        else:
            block_table.append(("Nonce", block.nonce))
            block_table.append(("Hash", block.block_hash.hex()))
            block_table.append(("Valid block", block.is_valid()))
            block_table.append(("Time of mining", block.time_of_creation))
            block_table.append(("Genesis Block", True))
        tx_tabulate = tabulate(
            tx_table, headers=["Block 🧱", f"ID: {block.id}"], tablefmt="fancy_grid")
        block_tabulate = tabulate(block_table, headers=["Block Data 📜", "Value"], tablefmt="fancy_grid")
        print(tx_tabulate)
        print("\n")
        print(block_tabulate)
        print(error_message(block.error))
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

        if index > max or index < 0:
            index = 0
