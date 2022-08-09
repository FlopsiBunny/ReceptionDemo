from twisted.internet import reactor, ssl, threads
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet.protocol import ServerFactory
from secrets import token_hex
import json, jsonpickle
from .data import *

class Server(Protocol):
    def __init__(self, console, offices, clients, devices):
        self.console = console
        self.offices = offices
        self.clients = clients
        self.devices = devices
        self.office = None
        self.token = token_hex(8)

    def sendNotice(self, notification):

        # Send Notification
        token = self.token
        notification.update_token(token)

        notifData = jsonpickle.encode(notification)
                        
        response = {
           "token": token,
           "payload": notifData
        }
        responseData = jsonpickle.encode(response)
        print("Sending...")
        reactor.callFromThread(self.transport.write, responseData.encode("utf-8"))
        self.transport.write(str("Tada").encode("utf-8"))
        self.console.log("Sending Notice to " + str(self._peer.host + ":" + str(self._peer.port)))
        print(responseData)
        print("Sent")
        

    def connectionMade(self):
        self._peer = self.transport.getPeer()
        self.clients[self.token] = self
        self.console.log("New Client Connected from " + str(self._peer.host + ":" + str(self._peer.port)))
        
    def dataReceived(self, data):

        data = data.decode("utf-8")
        try:
            jsonData = jsonpickle.decode(data)

            # Office Class Sent
            if isinstance(jsonData, ConnectionOperator):

                # Check for Access Token
                if jsonData.token != None and jsonData.token in self.devices:

                    self.clients[jsonData.token] = self
                    del self.clients[self.token]
                    self.token = jsonData.token

                    self.console.log("Allowed device.")
                    request = ConnectionOperator(token=jsonData.token, access=True)
                    requestData = jsonpickle.encode(request)
                    self.transport.write(requestData.encode("utf-8"))

                    if self.office == None:
                        for office in self.offices:
                            if office != "DEFAULT":
                                if self.offices.get(office, "token") == jsonData.token:
                                    newOffice = Office()
                                    newOffice.name = self.offices.get(office, "name")
                                    newOffice.token = jsonData.token
                                    newOffice.id = office
                                    self.office = newOffice
                                    break
                    officeData = jsonpickle.encode(self.office)
                    
                    response = {
                        "token": jsonData.token,
                        "payload": officeData
                        }
                    responseData = jsonpickle.encode(response)
                    self.transport.write(responseData.encode("utf-8"))

                    # Send Notification
                    notif = Notification("Test Notif", "This is a test of the system.", token=jsonData.token)
                    notifData = jsonpickle.encode(notif)
                    
                    response = {
                        "token": jsonData.token,
                        "payload": notifData
                        }
                    responseData = jsonpickle.encode(response)
                    self.transport.write(responseData.encode("utf-8"))

                    # Send Notification
                    notif = Notification("Test", "This is second a test of the system.", token=jsonData.token)
                    notifData = jsonpickle.encode(notif)
                    
                    response = {
                        "token": jsonData.token,
                        "payload": notifData
                        }
                    responseData = jsonpickle.encode(response)
                    self.transport.write(responseData.encode("utf-8"))
                else:
                    print("TOKEN: " + str(jsonData.token))
                    print("TOKENS: " + str(self.devices))
                    self.console.log("Requesting Setup Information...")

                    # Request Object
                    request = ConnectionOperator(token=jsonData.token, request=True)
                    jsonData = jsonpickle.encode(request)
                    self.transport.write(jsonData.encode("utf-8"))

                    self.console.log("Sent Request.")
            elif isinstance(jsonData, Office):
                self.console.log("Received Office Log...")
                if jsonData.setup:

                    self.office = jsonData
                    self.office.setup = False

                    self.console.log("Setup office.")
                    accessToken = token_hex(8)

                    self.office.token = accessToken
                    self.office.dump_config(self.offices)
                    
                    request = ConnectionOperator(token=accessToken, request=False)
                    jsonData = jsonpickle.encode(request)

                    self.devices.append(accessToken)
                    self.transport.write(jsonData.encode("utf-8"))
                else:
                    # Do Something
                    pass
                
                
        except json.decoder.JSONDecodeError:
            self.console.warning("Client Sent Str not JSON Bytes [" + self.token + "]: " + data)
            return
        
    def connectionLost(self, reason=connectionDone):
        if self.console != None:
            self.console.log("Closed Connection from Client: " + self.token)
        del self.clients[self.token]
        
class Factory(ServerFactory):
    def __init__(self, console, offices):
        self.console = console
        self.offices = offices
        self.clients = {}
        self.allowedDevices = []

        for office in self.offices:
            if office != "DEFAULT":
                print(office)
                token = self.offices.get(office, "token")
                print(token)
                self.allowedDevices.append(token)
                print(self.allowedDevices)
    
    def buildProtocol(self, addr):
        return Server(self.console, self.offices, self.clients, self.allowedDevices)

    def send_global_notice(self, notification):

        # Send Notification
        for clientToken in self.clients:
            client = self.clients[clientToken]
            reactor.callFromThread(client.sendNotice, notification)
