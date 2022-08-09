import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog

from lib.console import Console
from lib.offices import OfficeManager
from lib.server import *

from twisted.internet import tksupport, reactor
from configparser import ConfigParser

class ReceptionConsole(Tk):

    def __init__(self, version):

        super().__init__()

        # Window Setup
        tksupport.install(self)
        self.title("Reception Console | Ver. " + str(version))
        self.iconbitmap(default="media/logo.ico")
        self.state("zoomed")
        self.protocol("WM_DELETE_WINDOW", self.safe_quit)

        # Tabs Setup
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=TOP, fill=BOTH, expand=True)

        # Console Setup
        self.console = Console(self)
        self.tabs.add(self.console, text="Server Console")
        
        self.console.info("This is a test.")
        self.console.info("Informational output...")
        self.console.warning("Some warning...About something.")
        self.console.error("Error handling.")
        self.console.success("All done.")

        # Office Manager Setup
        self.officeManager = OfficeManager(self)
        self.tabs.add(self.officeManager, text="Office Management")

        # Menubar Setup
        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        self.officeMenu = Menu(self, tearoff=0)
        self.officeMenu.add_command(label="Send Global Notice", command=self.officeManager.new_global_notice)
        self.officeMenu.add_command(label="Send Office Notice")
        self.officeMenu.add_separator()
        self.officeMenu.add_command(label="Manage Offices...")
        self.menubar.add_cascade(menu=self.officeMenu, label="Offices")

        # Configuration Setup
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists("data/offices.rcf"):
            configFile = open("data/offices.rcf", "w")
            configFile.close()
        self.offices = ConfigParser()
        self.offices.read("data/offices.rcf")
        for office in self.offices:
            print(office)

        # Auto-Start Server
        self.start_server()

        # Window & Reactor Loop
        self.mainloop()

    def safe_quit(self):
        self.console.warning("Quiting...")
        
        # Save Data to Configuration File
        with open("data/offices.rcf", "w") as officesFile:
            self.offices.write(officesFile)
            officesFile.close()
        
        if reactor.running:
            reactor.stop()
        self.destroy()

    def start_server(self):
        if not reactor.running:
            self.console.log("Starting server...")
            self.factory = Factory(self.console, self.offices)
            self.factory.protocol = Server
            reactor.listenSSL(9800, self.factory, ssl.DefaultOpenSSLContextFactory("keys/server.key", "keys/server.crt"))
            self.console.log("Listening on 0.0.0.0:9800...")
            reactor.run()
        else:
            messagebox.showinfo("Start Server", "The server is already running.")


if __name__ == "__main__":
    ReceptionConsole(0.1)
