from twisted.internet import reactor, ssl, tksupport
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory as ClFactory
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from .data import *
import os, json

class Client(Protocol):
    def __init__(self, window):
        self.authenticated = False
        self.token = None
        self.officeRunning = False
        self.window = window
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
        elif isinstance(jsonData, Ping):

            ping = jsonData
            ping.reply()

            pingData = jsonpickle.encode(ping)
            self.transport.write(pingData.encode("utf-8"))
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
        self.window.title(str(jsonObject.name) + " - Connected")

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

    def __init__(self, window):
        self.window = window
    
    def buildProtocol(self, addr):
        return Client(self.window)

    def clientConnectionFailed(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print(reason)
        ClFactory.clientConnectionLost(self, connector, reason)
