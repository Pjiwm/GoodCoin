from cli import MainMenu
from cli import Utils
from core.Transaction import Tx
from core.Signature import *
from globals import manager
from core.Signature import *

while True:
    Utils.clear_screen()
    MainMenu.menu()

# manager.register_user("Test4002", "Test4002")
# print("Done")

# import time
# while True:
#     print(manager.address_book)
#     print(manager.server.is_running)
#     manager.populate_from_server()
#     time.sleep(1)