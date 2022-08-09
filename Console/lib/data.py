import jsonpickle, uuid
from tkinter import messagebox

class ConnectionOperator:
    def __init__(self, token=None, request=False, access=False):
        self.token = token
        self.request = request
        self.access = access

class Tenant:

    def __init__(self, first_name, last_name):

        self.first_name = first_name
        self.last_name = last_name

class Notification:

    def __init__(self, title, message, token=None):

        self.title = title
        self.message = message
        self.recepient_token = token

    def show(self, token=None):
        print(self.recepient_token)
        print(token)
        if token == self.recepient_token or self.recepient_token == None:
            messagebox.showinfo(self.title, self.message)

    def update_token(self, token):
        self.recepient_token = token

class Office:

    def __init__(self):

        self.id = 0
        self.name = "Office " + str(self.id)
        self.tenant = None
        self.token = None
        self.setup = True
        self.deviceUUID = str(uuid.UUID(int=uuid.getnode()).hex)

    def add_tenant(self, tenant):
        self.tenant = tenant

    def to_json(self):
        return jsonpickle.encode(self)

    def dump_config(self, config):

        if not config.has_section(self.id):
            config.add_section(self.id)

        config.set(str(self.id), "name", self.name)
        config.set(str(self.id), "token", str(self.token))
        config.set(str(self.id), "tenant", jsonpickle.encode(self.tenant))
