import os
from globals import manager
from colorama import Fore, Style
from core.Transaction import Tx
from tabulate import tabulate
from core.TxType import TxType
from core.TxBlock import REQUIRED_FLAG_COUNT

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def auto_update():
    messages = []
    removed_invalid = error_message(manager.tx_pool.remove_invalid(manager.pub_k))
    flagged_invalid = error_message(manager.tx_pool.move_invalid())
    flag_msg = manager.add_flag_to_block()
    removed_invalid_block = len(manager.block.invalid_flags) == REQUIRED_FLAG_COUNT
    approved_valid_block = len(manager.block.valid_flags) == REQUIRED_FLAG_COUNT
    if removed_invalid:
        messages.append(error_message(removed_invalid))
    if flag_msg:
        messages.append(info_message(flag_msg))
    if flagged_invalid:
        messages.append(error_message(flagged_invalid))
    if removed_invalid_block:
        messages.append(error_message(f"Removed last block because {REQUIRED_FLAG_COUNT} flagged it as invalid."))
    elif approved_valid_block:
        messages.append(success_message(f"Approved of last block because {REQUIRED_FLAG_COUNT} flagged it as valid."))
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


def tx_printer(transaction: Tx, pubk_username_dict: dict, show_balance=False):
    data = []
    for input in transaction.inputs:
        record = cyan_message(
            str(pubk_username_dict[input[0]])), error_message(str(-input[1]))
        data.append(record)
    for output in transaction.outputs:
        record = cyan_message(
            str(pubk_username_dict[output[0]])), success_message(str(output[1]))
        data.append(record)
    if transaction.type == TxType.Normal:
        data.append((info_message("TRANSACTION FEE"),
                    info_message(str(transaction.calc_tx_fee()))))
    else:
        data.append((info_message("REWARD TRANSACTION"), "-----"))
    table = tabulate(
        data, headers=[info_message("User📦"), info_message("Value 💰")], tablefmt="fancy_grid")
    print(table)
