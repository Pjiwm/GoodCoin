import sys
from cli.Utils import *
import inquirer
from core.BlockchainManager import BlockchainManager
from globals import manager

def exit():
    sys.exit(0)


def register():
    while True:
        form = [
            inquirer.Text("user", message="Please enter your username",
                          validate=lambda _, x: x != "."),
            inquirer.Password(
                "password", message="Please enter your password"),
            inquirer.Password("confirmpassword",
                              message="Please confirm your password"),
            inquirer.Confirm(
                "confirm",
                message="Do you confirm the creation of your account?",
                default=False,
            ),
        ]
        answers = inquirer.prompt(form)
        if not answers.get("confirm"):
            break
        if answers.get("password") != answers.get("confirmpassword"):
            print("Passwords did not match!")
        result = manager.register_user(
            answers.get("user"), answers.get("password"))
        if not result:
            print("Successfully registered!")
            break
        else:
            print(result)
            option = inquirer.list_input(
                "Want to try again?", choices=["Yes", "No"])
            if option == "No":
                break


def login():
    while True:
        form = [
            inquirer.Text("user", message="Please enter your username",
                          validate=lambda _, x: x != "."),
            inquirer.Password(
                "password", message="Please enter your password"),
        ]
        answers = inquirer.prompt(form)
        result = manager.login_user(
            answers.get("user"), answers.get("password"))
        if not result:
            break
        else:
            print(result)
            option = inquirer.list_input(
                "Want to try again?", choices=["Yes", "No"])
            if option == "No":
                break

def logout():
    manager.logout_user()



def menu():
    title_1 = """
  ________                  .___
 /  _____/  ____   ____   __| _/
/   \  ___ /  _ \ /  _ \ / __ |
\    \_\  (  <_> |  <_> ) /_/ |
 \______  /\____/ \____/\____ |
        \/   COIN            \/
    """
    print(title_1)
    print(manager.address_book)
    menu_mapping = {}
    if manager.username:
        print(f"Welcome {manager.username}!")
        menu_mapping["Logout"] = logout
        menu_mapping["Exit"] = exit
    else:
        menu_mapping["Register"] = register
        menu_mapping["Login"] = login
        menu_mapping["Exit"] = exit

    option = inquirer.list_input("Main Menu", choices=menu_mapping.keys())
    clear_screen()
    menu_mapping.get(option)()
