import sys
from cli.Utils import *
from InquirerPy import inquirer
from cli.TransactionMenu import *
from cli.BlockchainMenu import *
from globals import manager


def exit():
    sys.exit(0)


def register():
    while True:
        user = inquirer.text(message="Please enter your username").execute()
        pw = inquirer.secret(message="Please enter your password").execute()
        pw_confirm = inquirer.secret(
            message="Please confirm your password").execute()
        confirm = inquirer.confirm(
            message="Do you confirm the creation of your account?", default=False).execute()
        if not confirm:
            break
        if pw != pw_confirm:
            print("Passwords do not match")
            continue
        if pw == pw_confirm:
            result = manager.register_user(
                user, pw)
            if not result:
                print("Successfully registered!")
                break
        else:
            print(result)
            option = inquirer.select(
                "Want to try again?", choices=["Yes", "No"])
            if option == "No":
                break


def login():
    while True:
        user = inquirer.text(message="Please enter your username").execute()
        pw = inquirer.secret(message="Please enter your password").execute()
        result = manager.login_user(
            user, pw)
        if not result:
            break
        else:
            print(result)
            option = inquirer.select(
                "Want to try again?", choices=["Yes", "No"]).execute()
            if option == "No":
                break


def logout():
    manager.logout_user()


def menu():
    title = """
 ██████   ██████   ██████  ██████       ██████  ██████  ██ ███    ██ 
██       ██    ██ ██    ██ ██   ██     ██      ██    ██ ██ ████   ██ 
██   ███ ██    ██ ██    ██ ██   ██     ██      ██    ██ ██ ██ ██  ██ 
██    ██ ██    ██ ██    ██ ██   ██     ██      ██    ██ ██ ██  ██ ██ 
 ██████   ██████   ██████  ██████       ██████  ██████  ██ ██   ████
    """
    print(unique_message(title))
    menu_mapping = {}
    if manager.username:
        print(f"Welcome {manager.username}!")
        print(f"Balance: GC {manager.calculate_balance()}")
        menu_mapping["Transactions"] = transaction_menu
        menu_mapping["Logout"] = logout
        menu_mapping["Explore Blockchain"] = show_blocks
        menu_mapping["Mine new block"] = mine_block
        menu_mapping["Exit"] = exit
        for msg in auto_update():
            print(msg)
    else:
        menu_mapping["Register"] = register
        menu_mapping["Login"] = login
        menu_mapping["Explore Blockchain"] = show_blocks
        menu_mapping["Exit"] = exit
    option = inquirer.select(
        "Main Menu", choices=menu_mapping.keys()).execute()
    clear_screen()
    menu_mapping.get(option)()
