from cli import MainMenu
from cli import Utils
from core.Transaction import Tx
from core.Signature import *
from globals import manager
from core.Signature import *

alex_prv, alex_pbc = generate_keys()
mike_prv, mike_pbc = generate_keys()
rose_prv, rose_pbc = generate_keys()
mara_prv, mara_pbc = generate_keys()

# Valid Transactions
Tx1 = Tx()
Tx1.add_input(alex_pbc, 5)
Tx1.add_output(rose_pbc, 5)
Tx1.sign(alex_prv)
Tx2 = Tx()
Tx2.add_input(mike_pbc,1)
Tx2.add_output(rose_pbc,0.9)
Tx2.sign(mike_prv)

while True:
    Utils.clear_screen()
    MainMenu.menu()
