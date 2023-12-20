from cli import MainMenu
from cli import Utils
from core.Transaction import Tx
from core.Signature import *
from globals import manager
from core.Signature import *
from p2p.Server import Server
from p2p.Client import Client
import time
while True:
    Utils.clear_screen()
    MainMenu.menu()

# myServer = Server()

# client = Client()

# client.add_recipient("localhost", myServer.port)

# tx: Tx = Tx()
# client.send_transaction(tx)
# time.sleep(1)
# print(myServer.tx_received)

# myServer.stop_server()