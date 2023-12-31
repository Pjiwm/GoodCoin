import os
from cli.Utils import *
from InquirerPy import inquirer
from cli.TransactionMenu import *
from cli.BlockchainMenu import *
from globals import manager
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption

def exit():
    manager.stop_server()
    os._exit(0)


def show_keys():
    print(f"Public key: \n{manager.pub_k.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)}")
    print("\n")
    print(f"Private key: \n{manager.priv_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())}")
    print("\n")
    inquirer.select("Press enter to go back", choices=["Go back"]).execute()

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
            print(error_message("Passwords do not match"))
            option = inquirer.select(
                    "Want to try again?", choices=["Yes", "No"])
            if option == "No":
                break
            continue
        if pw == pw_confirm:
            result = manager.register_user(
                user, pw)
            if not result:
                print("Successfully registered!")
                break
            else:
                print(error_message(result))
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
        print(f"Welcome {info_message(manager.username)}!")
        print(f"Balance: GC {unique_message(str(round(manager.calculate_balance(), 1)))}")
        menu_mapping["Transactions"] = transaction_menu
        menu_mapping["Logout"] = logout
        menu_mapping["Explore Blockchain"] = show_blocks
        menu_mapping["Mine new block"] = mining_menu
        menu_mapping["Show keys"] = show_keys
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
