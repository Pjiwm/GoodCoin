from cli import MainMenu
from cli import Utils
from globals import manager
while True:
    if manager.sync_manager.blocks_done:
        Utils.clear_screen()
        MainMenu.menu()
