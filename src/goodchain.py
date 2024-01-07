from cli import MainMenu
from cli import Utils
from globals import manager
from InquirerPy import inquirer
synced_data = False
while True:
    if manager.ready:
        if not synced_data:
            synced_data = manager.add_synced_data()
            inquirer.select("Press ENTER to continue:", choices=["go to wallet"]).execute()
        Utils.clear_screen()
        MainMenu.menu()