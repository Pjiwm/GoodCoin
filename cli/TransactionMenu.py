from globals import manager
from cli.Utils import clear_screen
from tabulate import tabulate
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator


def address_book():
    while True:
        clear_screen()
        page = 1
        items_per_page = 10
        headers = ["Number", "Users 🔑"]
        min = (page - 1) * items_per_page
        max = page * items_per_page
        data = list(manager.address_book.keys())[min:max]
        numbered_data = [[i + 1, user] for i, user in enumerate(data)]
        table = tabulate(numbered_data, headers=headers, tablefmt="fancy_grid")
        print(table)
        table_options = ["Next Page", "Previous Page", "Back"]
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


def transact():
    clear_screen()
    tx = manager.get_transaction_builder()
    while True:
        completer = {k: None for k, _ in manager.address_book.items()}
        recipient = inquirer.text(
            message="To who do you want to transfer coins",
            completer=completer,
            multicolumn_complete=True,
        ).execute()

        coin_input = inquirer.text(
            message="How many coins do you want to send?",
            validate=NumberValidator()).execute()
        coins = round(float(coin_input), 1)

        transaction_fee_input = inquirer.text(
            message="What is the transaction fee you want to pay?",
            validate=NumberValidator()).execute()
        transaction_fee = round(float(transaction_fee_input), 1)
        tx.add_input(manager.pub_k, coins + transaction_fee)
        tx.add_output(manager.address_book[recipient], coins)

        choices = ["Add a required signature", "Cancel transaction", "Try again", "Proceed"]
        next_step = inquirer.select(
            "Please select what to do next", choices=choices).execute()
        if next_step == choices[0]:
            reqd = inquirer.text(
                message="Select who needs to sign the transaction",
                completer=completer,
                multicolumn_complete=True,
            ).execute()
            tx.add_reqd(manager.address_book[reqd])
        elif next_step == choices[1]:
            return
        elif next_step == choices[2]:
            continue
        tx.sign(manager.priv_key)
        manager.make_transaction(tx)
        return


def transaction_menu():
    while True:
        title = """
        ████████ ██████   █████  ███    ██ ███████  █████   ██████ ████████ ██  ██████  ███    ██ ███████ 
           ██    ██   ██ ██   ██ ████   ██ ██      ██   ██ ██         ██    ██ ██    ██ ████   ██ ██      
           ██    ██████  ███████ ██ ██  ██ ███████ ███████ ██         ██    ██ ██    ██ ██ ██  ██ ███████ 
           ██    ██   ██ ██   ██ ██  ██ ██      ██ ██   ██ ██         ██    ██ ██    ██ ██  ██ ██      ██ 
           ██    ██   ██ ██   ██ ██   ████ ███████ ██   ██  ██████    ██    ██  ██████  ██   ████ ███████ 
        """
        print(title)
        menu_mapping = {
            "Address Book": address_book,
            "Make transaction": transact,
            "Back": None
        }
        option = inquirer.select(
            "Transaction Menu", choices=menu_mapping.keys()).execute()
        clear_screen()
        result = menu_mapping.get(option)
        if result is not None:
            result()
            clear_screen()
        else:
            return
