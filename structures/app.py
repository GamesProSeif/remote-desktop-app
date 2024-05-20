from pickle import dumps
from random import choice
from twisted.internet import reactor, tksupport
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from structures.protocol import TCPFactory
from structures.input_handling import InputHandling
from structures.handling_recieve import MouseKeyboardHandler
from .auth_handler import AuthHandler
from socket import gethostname, gethostbyname_ex


class App:
    def __init__(self):
        self.debug = False
        self.mode = None
        self.protocol = None
        self._handlers = {}
        self._listeners = []
        self.host = self.get_host()
        self.port = 5005
        self.running = False
        self.pass_code = None
        self.authenticated = False

    def setMode(self, mode):
        if mode == "server" or mode == "client":
            self.mode = mode
        else:
            raise Exception(f"Invalid mode: {mode}")

    def addHandler(self, event_name, fn):
        self._handlers[event_name] = fn

    def useHandler(self, event_name, *args):
        self._handlers[event_name](*args)

    def addListener(self, listener):
        self._listeners.append(listener)

    def listen(self):
        for listener in self._listeners:
            reactor.callInThread(listener)

    def startGUI(self, gui):
        tksupport.install(gui.server_root if self.mode == "server" else gui.client_root)

    def send(self, event, *args):
        msg = dumps({"event": event, "args": args})
        self.protocol.transport.write(msg)

    def start(self):
        self.running = True
        if self.mode == "server":
            mouseKeyboardHandler = MouseKeyboardHandler()
            authHandler = AuthHandler()
            self.addHandler("AUTH", authHandler.attempt_connection)
            self.addHandler("MOUSE", mouseKeyboardHandler.mouse)
            self.addHandler("KEYBOARD", mouseKeyboardHandler.keyboard)

            endpoint = TCP4ServerEndpoint(reactor, self.port)
            endpoint.listen(TCPFactory(self))
            if self.debug:
                print("DEBUG: Started TCP Server")
        elif self.mode == "client":
            inputhandling = InputHandling(self)
            self.addListener(inputhandling.start)

            endpoint = TCP4ClientEndpoint(reactor, self.host, self.port)
            endpoint.connect(TCPFactory(self))
            if self.debug:
                print("DEBUG: Started TCP Client")
        else:
            raise Exception(f"Invalid mode: {self.mode}")

        self.listen()
        reactor.run()

    def stop(self):
        if self.running:
            reactor.stop()
            self.running = False
        exit()

    def generate_pass_code(self):
        digits = "0123456789abcdef"
        code = ""
        for _ in range(6):
            code += choice(digits)
        self.pass_code = code
        return code

    def get_link(self):
        return f"{self.host}?p={self.pass_code}"

    def get_host(self):
        ips = gethostbyname_ex(gethostname())[2]
        for ip in ips:
            if ip.split(".")[2] == "1":
                return ip
        return ips[1]
