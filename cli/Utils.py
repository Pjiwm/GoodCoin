import os
from globals import manager
from colorama import Fore, Style
from core.Transaction import Tx
from tabulate import tabulate


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

def tx_printer(transaction: Tx, pubk_username_dict: dict):
     data = []
     for input in transaction.inputs:
         record = cyan_message(
             str(pubk_username_dict[input[0]])), error_message(str(-input[1]))
         data.append(record)
     for output in transaction.outputs:
         record = cyan_message(
             str(pubk_username_dict[output[0]])), success_message(str(output[1]))
         data.append(record)
     data.append((info_message("TRANSACTION FEE"),
                 info_message(str(transaction.calc_tx_fee()))))
     table = tabulate(
         data, headers=[info_message("User📦"), info_message("Value 💰")], tablefmt="fancy_grid")
     print(table)