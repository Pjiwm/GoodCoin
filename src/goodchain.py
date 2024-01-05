from cli import MainMenu
from cli import Utils
from globals import manager
while True:
    if manager.ready:
        Utils.clear_screen()
        MainMenu.menu()