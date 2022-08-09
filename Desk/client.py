from twisted.internet import reactor, ssl, tksupport
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from lib.data import *
from tkinter import *
from tkinter import ttk
import json, os, time

class SetupWindow(Tk):

    def __init__(self, callback):

        super().__init__()

        self.callback = callback

        # Window Setup
        self.title("Setup Office")
        #self.iconbitmap(default="media/logo.icon")
        self.geometry("300x300")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Setup Information Window
        officeIDFrame = ttk.LabelFrame(self, text="Office ID")
        officeIDFrame.grid(row=0, column=0, sticky=N, pady=20)
        officeNameFrame = ttk.LabelFrame(self, text="Office Name")
        officeNameFrame.grid(row=0, column=1, sticky=N, pady=20)

        self.officeName = StringVar()
        officeNameEntry = ttk.Entry(officeNameFrame, width=20, textvariable=self.officeName)
        officeNameEntry.pack()

        self.officeID = StringVar()
        officeIDEntry = ttk.Entry(officeIDFrame, width=5, textvariable=self.officeID)
        officeIDEntry.pack()
        
        # Window Mainloop
        self.protocol("WM_DELETE_WINDOW", self.finish_exit)
        self.mainloop()

    def finish_exit(self):
        office = Office()
        office.id = self.officeID.get()
        office.name = self.officeName.get()

        self.callback(jsonpickle.encode(office))
        tksupport.uninstall()
        self.destroy()

class OfficeDesk(Tk):

    def __init__(self, office):
        super().__init__()

        # Window Setup
        tksupport.install(self)
        self.title(str(office.id) + " | " + office.name)
        self.state("zoomed")

        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.mainloop()

    def quit(self):

        tksupport.uninstall()
        self.destroy()
        reactor.stop()
        

class Client(Protocol):
    def __init__(self):
        self.authenticated = False
        self.token = None
        self.officeRunning = False
        #reactor.callInThread(self.send_data)

    def connectionMade(self):
        self.setup()
        
    def dataReceived(self, data):
        
        data = data.decode("utf-8")
        print(data)
        try:
            jsonData = jsonpickle.decode(data)
        except json.decoder.JSONDecodeError:
            print(data)
            return
        if isinstance(jsonData, ConnectionOperator):

            if jsonData.request:
                setup = SetupWindow(self.setup_client)
            else:
                if jsonData.access:
                    self.token = jsonData.token
                    print("Access Token: " + jsonData.token)
                    self.authenticated = True
                    if os.path.exists(os.getcwd() + "/token.key"):
                        tokenFile = open("token.key", "w")
                        tokenFile.write(jsonData.token)
                        tokenFile.close()
                else:
                    
                    # Verify Request
                    request = ConnectionOperator(token=jsonData.token)
                    jsonData = jsonpickle.encode(request)
                    self.transport.write(jsonData.encode("utf-8"))
        elif isinstance(jsonData, dict):

            # Verify Correct Token
            if jsonData["token"] != self.token:
                print("Invalid data sent.")
                return

            # Get Payload
            payload = jsonData["payload"]

            jsonObject = jsonpickle.decode(jsonData["payload"])

            # Payload Detection
            if isinstance(jsonObject, Office):
                if not self.officeRunning:
                    reactor.callFromThread(self.start_desk, jsonObject)
            elif isinstance(jsonObject, Notification):
                jsonObject.show(token=jsonData["token"])
                
        print(data)

    def start_desk(self, jsonObject):
        self.officeRunning = True
        desk = OfficeDesk(jsonObject)

    def setup(self):
        # Load Previous Token
        if os.path.exists(os.getcwd() + "/token.key"):
            token = open("token.key", "r").read()
        else:
            token = None
        print(token)

        connection = ConnectionOperator(token=token)
                
        jsonData = jsonpickle.encode(connection)
        self.transport.write(jsonData.encode("utf-8"))
                
        print(jsonData)
        
    def send_data(self):
        while True:
            cmd = input("Content: ")
            if cmd == "quit":
                reactor.stop()
                break
            elif cmd == "setup":
                self.setup()
            elif cmd == "office":
                
                # Process JSON Data
                office = Office()
                office.id = 1
                office.name = "Kowhai Room"

                print(office.to_json())
                self.transport.write(office.to_json().encode("utf-8"))
            else:
                self.transport.write(cmd.encode("utf-8"))

    def setup_client(self, data):

        self.transport.write(data.encode("utf-8"))
        print(data)

class Factory(ClFactory):
    protocol = Client
    
    def buildProtocol(self, addr):
        return Client()

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionLost(self, connector, reason)
        
if __name__ == "__main__":
    factory = Factory()
    reactor.connectSSL('localhost', 9800, factory, ssl.ClientContextFactory())
    reactor.run()
