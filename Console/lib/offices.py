from tkinter import *
from tkinter import ttk
from twisted.internet import tksupport, reactor

from .data import *

class OfficeManager(Frame):

    def __init__(self, parent):

        super().__init__(parent, height=1000)

        # Define Variables
        self.parent = parent

        # Treeview Setup
        self.managerScroll = Scrollbar(self)
        self.manager = ttk.Treeview(self, yscrollcommand=self.managerScroll.set)
        self.managerScroll["command"] = self.manager.yview

        self.manager["columns"] = ("#1", "#2")
        self.manager.heading("#0", text="Room ID")
        self.manager.heading("#1", text="Room Name/Title")
        self.manager.heading("#2", text="Current Tenant")

        # Pack Widgets
        self.managerScroll.pack(side=RIGHT, fill=Y)
        self.manager.pack(side=TOP, fill=BOTH, expand=True)

    def new_global_notice(self, *args):

        nm = NoticeManager(self.parent)
        

class NoticeManager(Toplevel):

    def __init__(self, parent, office=None):

        super().__init__(parent)

        # Define Variables
        self.parent = parent
        self.office = office

        # Window Setup
        tksupport.install(self)
        if office == None:
            self.title("Send Notice - All Offices")
        else:
            self.title("Send Notice - " + office.id)

        # Notifcation Input Setup
        self.title = StringVar()
        self.message = StringVar()

        self.titleEntry = Text(self, width=100, height=1)
        self.messageEntry = Text(self, width=100, height=5)

        self.titleEntry.pack(side=TOP, pady=10)
        self.messageEntry.pack(side=TOP, pady=10, padx=20)

        self.submit = ttk.Button(self, text="Send", command=self.submit)
        self.submit.pack(side=TOP, anchor=E, pady=10, padx=20)

        # Window Loop
        self.mainloop()

    def submit(self, *args):

        # Submit Notification to Server
        title = self.titleEntry.get("1.0", END)
        message = self.messageEntry.get("1.0", END)

        # Notification Setup
        notif = Notification(title, message)

        # Send Notification
        if self.office == None:
            self.parent.factory.send_global_notice(notif)

        # Destroy Window
        self.destroy()
