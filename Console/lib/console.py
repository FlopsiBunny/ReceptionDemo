from tkinter import *
from datetime import datetime

class Console(Frame):

    def __init__(self, parent):

        super().__init__(parent, height=1000)

        # Console Setup
        self.scrollbar = Scrollbar(self)
        self.console = Text(self, fg="white", bg="black", yscrollcommand=self.scrollbar.set, state="disabled")
        self.scrollbar["command"] = self.console.yview

        # Console Tags
        self.console.tag_configure("info", foreground="lightblue")
        self.console.tag_configure("error", foreground="red")
        self.console.tag_configure("success", foreground="green")
        self.console.tag_configure("warning", foreground="yellow")

        # Command Line Setup
        self.commandFrame = Frame(self)
        self.command = StringVar()
        self.commandLabel = Label(self.commandFrame, fg="white", bg="black", text="$")
        self.commandLine = Entry(self.commandFrame, fg="white", bg="black", textvariable=self.command)

        self.commandLine.bind("<Return>", self._command)

        # Pack Widgets
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.commandLabel.pack(side=LEFT, anchor=S)
        self.commandLine.pack(side=BOTTOM, fill=X)
        self.commandFrame.pack(side=BOTTOM, fill=X)
        
        self.console.pack(side=TOP, fill=BOTH, expand=True)

    def _command(self, *args):

        command = self.command.get()
        if command != "":
            self.command.set("")

            self.info("Executing " + command)

    def log(self, message, tag="info"):
        timestamp = datetime.now().strftime("%d %b %Y %H:%M:%S")
        self.console["state"] = "normal"
        self.console.insert(END, "[")
        self.console.insert(END, tag.capitalize(), (tag))
        self.console.insert(END, "]")
        self.console.insert(END, "[" + timestamp + "] " + message + "\n")
        self.console["state"] = "disabled"

    def info(self, message):
        self.log(message)

    def error(self, message):
        self.log(message, tag="error")

    def success(self, message):
        self.log(message, tag="success")

    def warning(self, message):
        self.log(message, tag="warning")
