from globals import manager
from cli.Utils import *
from core.Transaction import Tx
from tabulate import tabulate
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.backends import default_backend



def show_txs_from_ledger():
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    last_block = manager.block
    list_of_txs = []
    user_bytes = manager.pub_k.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    while last_block:
        for tx in last_block.data:
            found_user = False
            for tx_user, _ in tx.inputs:
                if tx_user == user_bytes:
                    found_user = True
            if found_user:
                list_of_txs.append((last_block.id, last_block.block_hash.hex(), tx, last_block.time_of_creation))
        last_block = last_block.previous_block

    if len(list_of_txs) == 0:
        return error_message("No transactions found on the ledger from you.")

    index = len(list_of_txs) - 1

    while True:
        clear_screen()
        tx_printer(list_of_txs[index][2], swapped_dict)
        print(f"Block: #{list_of_txs[index][0]}")
        print(f"Block hash: {info_message(list_of_txs[index][1])}")
        print(f"Block time of creation: {list_of_txs[index][3]}")
        print(f"Transaction {index+1}/{len(list_of_txs)}")
        options = ["Next Transaction", "Previous Transaction", "Back"]
        option = inquirer.select("Transaction", choices=options).execute()
        if option == options[0]:
            index += 1
        elif option == options[1]:
            index -= 1
        else:
            return
        if index > len(list_of_txs) - 1 or index < 0:
            index = 0

def address_book():
    page = 1
    while True:
        clear_screen()
        items_per_page = 10
        headers = [info_message("Number"), info_message("Users 🔑")]
        min = (page - 1) * items_per_page
        max = page * items_per_page
        data = list(manager.address_book.keys())[min:max]
        numbered_data = [[i + 1, cyan_message(user)]
                         for i, user in enumerate(data)]
        table = tabulate(numbered_data, headers=headers, tablefmt="fancy_grid")
        print(table)
        table_options = ["Next Page", "Previous Page", "Back"]
        print(f"Page #{page}")
        option = inquirer.select(
            "Adress book", choices=table_options).execute()
        if option == "Next Page":
            page += 1
        elif option == "Previous Page":
            page -= 1
        else:
            return

        if max > len(manager.address_book.keys()) or page < 1:
            page = 1


def cancel_transaction():
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    index = 0
    transactions = manager.tx_pool.get_users_txs(manager.pub_k)
    if not transactions:
        return error_message("No transactions to cancel.")
    while True:
        clear_screen()

        transaction = transactions[index]
        tx_printer(transaction, swapped_dict)
        if not transaction.is_valid():
            print("Invalid transaction:")
            for error in transaction.invalidations:
                print(error_message(" -", error))
        print(f"Transaction {index+1}/{len(transactions)}")

        table_options = ["Next Transaction",
                         "Previous Transaction", "Cancel Transaction", "Back"]
        option = inquirer.select(
            "Adress book", choices=table_options).execute()
        if option == table_options[0]:
            index += 1
        elif option == table_options[1]:
            index -= 1
        elif option == table_options[2]:
            return manager.tx_pool.cancel_transaction(manager.pub_k, transaction)
        else:
            return

        if index >= len(transactions) or index < 0:
            index = 0


def show_tx_pool():
    swapped_dict = {v.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo): k for k, v in manager.address_book.items()}
    index = 0
    if not manager.tx_pool.transactions:
        return error_message("No transactions in pool.")
    while True:
        clear_screen()

        transaction = manager.read_transaction(index)
        tx_printer(transaction, swapped_dict, show_balance=True)
        if not transaction.is_valid():
            print("Invalid transaction:")
            for error in transaction.invalidations:
                print(" -", error)
        print(f"Transaction {index+1}/{len(manager.tx_pool.transactions)}")

        table_options = ["Next Transaction", "Previous Transaction", "Back"]
        option = inquirer.select(
            "Adress book", choices=table_options).execute()
        if option == table_options[0]:
            index += 1
        elif option == table_options[1]:
            index -= 1
        else:
            return

        if index >= len(manager.tx_pool.transactions) or index < 0:
            index = 0

def __transaction_value_validator(value):
    try:
        num = float(value)
        if int(num * 10) != num * 10:
            return False
    except:
        return False
    return True

def transact():
    clear_screen()
    while True:
        tx = Tx()
        completer = {k: None for k, _ in manager.address_book.items()}
        completer["EXIT"] = None
        recipient = inquirer.text(
            message="To who do you want to transfer coins, type EXIT to exit.",
            completer=completer,
            invalid_message="Invalid recipient. Please select an existing user.",
            multicolumn_complete=True,
            validate=lambda x: x in completer.keys()
        ).execute()
        if recipient == "EXIT":
            return

        coin_input = inquirer.text(
            message="How many coins do you want to send?",
            invalid_message="Please enter a valid number with up to one decimal place (seperated by '.').",
            validate=__transaction_value_validator).execute(),
        coins = round(float(coin_input[0]), 1)

        transaction_fee_input = inquirer.text(
            message="What is the transaction fee you want to pay?",
            invalid_message="Please enter a valid number with up to one decimal place (seperated by '.').",
            validate=__transaction_value_validator).execute()
        transaction_fee = round(float(transaction_fee_input), 1)


        if manager.calculate_balance() - coins - transaction_fee < 0:
            choices = ["Try again", "Go back"]
            next_step = inquirer.select(
                "Insufficient balance", choices=choices).execute()
            if next_step == choices[0]:
                continue
            elif next_step == choices[1]:
                return

        tx.add_input(manager.pub_k, coins + transaction_fee)
        try:
            tx.add_output(manager.address_book[recipient], coins)
        except:
            tx.add_output(None, coins)

        choices = ["Cancel transaction", "Try again", "Proceed"]
        next_step = inquirer.select(
            "Please select what to do next", choices=choices).execute()
        if next_step == choices[0]:
            return
        elif next_step == choices[1]:
            continue
        tx.sign(manager.priv_key)
        manager.make_transaction(tx)
        return success_message("Transaction completed.")


def transaction_menu():
    msg = ""
    while True:
        title = """
████████ ██████   █████  ███    ██ ███████  █████   ██████ ████████ ██  ██████  ███    ██ ███████ 
   ██    ██   ██ ██   ██ ████   ██ ██      ██   ██ ██         ██    ██ ██    ██ ████   ██ ██      
   ██    ██████  ███████ ██ ██  ██ ███████ ███████ ██         ██    ██ ██    ██ ██ ██  ██ ███████ 
   ██    ██   ██ ██   ██ ██  ██ ██      ██ ██   ██ ██         ██    ██ ██    ██ ██  ██ ██      ██ 
   ██    ██   ██ ██   ██ ██   ████ ███████ ██   ██  ██████    ██    ██  ██████  ██   ████ ███████ 
        """
        print(unique_message(title))
        print(f"Welcome {info_message(manager.username)}!")
        print(
            f"Balance: GC {unique_message(str(round(manager.calculate_balance(), 1)))}")
        if msg:
            print(msg)
        for txt in auto_update():
            print(txt)
        menu_mapping = {
            "Address Book": address_book,
            "Make transaction": transact,
            "Transaction Pool": show_tx_pool,
            "Cancel transaction": cancel_transaction,
            "My transactions": show_txs_from_ledger,
            "Back": None
        }
        option = inquirer.select(
            "Transaction Menu", choices=menu_mapping.keys()).execute()
        clear_screen()
        result = menu_mapping.get(option)
        if result is not None:
            msg = result()
            clear_screen()
        else:
            return
