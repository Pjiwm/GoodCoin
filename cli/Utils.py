import os
from globals import manager
from colorama import Fore, Style


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def auto_update():
    messages = []
    invalid_txs = error_message(manager.tx_pool.remove_invalid(manager.pub_k))
    flag_msg = manager.add_flag_to_block()
    if invalid_txs:
        messages.append(error_message(invalid_txs))
    if flag_msg:
        messages.append(info_message(flag_msg))
    return messages


def error_message(string: str):
    return Fore.RED + string + Style.RESET_ALL if string else ""

def success_message(string: str):
    return Fore.GREEN + string + Style.RESET_ALL if string else ""

def unique_message(string: str):
    return Fore.MAGENTA + string + Style.RESET_ALL if string else ""

def info_message(string: str):
    return Fore.YELLOW + string + Style.RESET_ALL if string else ""

def cyan_message(string: str):
    return Fore.CYAN + string + Style.RESET_ALL if string else ""