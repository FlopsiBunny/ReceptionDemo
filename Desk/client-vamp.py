# Import Modules
from tkinter import *
from lib.data import *
from lib.server import *

from twisted.internet import tksupport, reactor

class OfficeWindow(Tk):

    def __init__(self, office):

        # Parent Init
        super().__init__()

        # Define Variables
        self.status = "Disconnected"

        # Window Setup
        tksupport.install(self)
        self.title(office.name + " - " + self.status)
        self.state("zoomed")

        factory = Factory(self)
        reactor.connectSSL('localhost', 9800, factory, ssl.ClientContextFactory())

        # Window Mainloop
        reactor.run()
        self.mainloop()

newOffice = Office()
newOffice.name = "Kowhai Room"
newOffice.token = ""
newOffice.id = 1
o = OfficeWindow(newOffice)
