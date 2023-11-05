from globals import manager
from cli.Utils import *
from tabulate import tabulate
from core.TxType import *
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from core.TxBlock import MAX_TX_AMOUNT
from InquirerPy import inquirer
import datetime


def mining_menu():
    clear_screen()
    print("Mining Menu")
    if len(manager.tx_pool.transactions) < 5:
        print(error_message(
            "Pool does currently not have enough transactions to mine a block."))
    wait_time = manager.block.timer_for_next_block(datetime.datetime.now())
    if wait_time > 0:
        print(error_message(
            f"Wait {wait_time} seconds before mining a block."))
    options = ["Optimal mine strategy", "Manual strategy", "Back"]
    option = inquirer.select(
        "Mining options", choices=options).execute()
    if option == options[0]:
        print(optimal_mine())
    elif option == options[1]:
        result = manual_mine_menu()
        if result:
            print(result)
        else:
            return
    else:
        return
    inquirer.select("Return to main menu:", choices=["proceed"]).execute()

def manual_mine_menu():
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    index = 0
    transactions = manager.tx_pool.transactions
    tx_to_mine = []
    # Add reward tx to mine by default
    reward_tx = manager.tx_pool.get_reward_tx()
    if reward_tx:
        tx_to_mine.append(reward_tx)
    if not transactions:
        return
    while True:
        clear_screen()
        print(f"Added transactions {len(tx_to_mine)}/{MAX_TX_AMOUNT}")
        tx_fee_sum = sum(tx.calc_tx_fee() for tx in transactions)
        print(f"Total transaction fee: {tx_fee_sum}")
        transaction = transactions[index]
        tx_printer(transaction, swapped_dict)

        if not transaction.is_valid():
            print("Invalid transaction:")
            for error in transaction.invalidations:
                print(error_message(" -", error))

        is_selected = False
        if any(transaction == tx for tx in tx_to_mine):
            print(success_message("Transaction selected 🎯"))
            is_selected = True

        print(f"Transaction {index+1}/{len(transactions)}")
        select_deselect = {
            True: "Deselect transaction",
            False: "Select transaction"
        }

        table_options = ["Next Transaction", "Previous Transaction",
                         select_deselect[is_selected], "Start mining", "Back"]

        option = inquirer.select(
            "Adress book", choices=table_options).execute()
        if option == table_options[0]:
            index += 1
        elif option == table_options[1]:
            index -= 1
        elif option == table_options[2]:
            if not is_selected:
                tx_to_mine.append(transaction)
            else:
                tx_to_mine.remove(transaction)
            continue
        elif option == table_options[3]:
            return manual_mine(tx_to_mine)
        else:
            return

        if index >= len(transactions) or index < 0:
            index = 0

def manual_mine(tx_list):
    clear_screen()
    print("Mining with manual strategy...")
    return manager.mine_block_manual(tx_list)

def optimal_mine():
    clear_screen()
    print("Mining with optimal strategy...")
    return manager.mine_block_optimal()

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

        if transactions == []:
            tx_table.append(("No transactions in this block", "-----"))

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
            tx_table.append(("Mining Reward ⛏️", TxType.Reward.value))
            miner_name = swapped_dict[block.miner]
            tx_table.append((miner_name, block.get_mining_reward()))
            block_table.append(("Nonce", block.nonce))
            block_table.append(("Hash", block.block_hash.hex()))
            block_table.append(
                ("Previous Hash", block.previous_block.block_hash.hex()))
            block_table.append(("Time of mining", block.time_of_creation))
            block_table.append(("Valid block", block.is_valid()))
            block_table.append((
                "Validation flags", f"Valid: {block.count_valid_flags()} Invalid: {block.count_invalid_flags()}"))
        else:
            block_table.append(("Nonce", block.nonce))
            block_table.append(("Hash", block.block_hash.hex()))
            block_table.append(("Valid block", block.is_valid()))
            block_table.append(("Time of mining", block.time_of_creation))
            block_table.append(("Genesis Block", True))
        tx_tabulate = tabulate(
            tx_table, headers=["Block 🧱", f"ID: {block.id}"], tablefmt="fancy_grid")
        block_tabulate = tabulate(block_table, headers=[
                                  "Block Data 📜", "Value"], tablefmt="fancy_grid")
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
