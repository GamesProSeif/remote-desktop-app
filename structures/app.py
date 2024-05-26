from pickle import dumps
from random import choice
from time import sleep
from twisted.internet import reactor, tksupport, defer
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from structures.protocol import TCPFactory
from structures.input_handling import InputHandling
from structures.handling_recieve import MouseKeyboardHandler
from structures.share_screen_handler import ScreenShareHandler
from .auth_handler import AuthHandler
from .file_handler import FileHandler
from socket import gethostname, gethostbyname_ex
from io import BytesIO


class App:
    def __init__(self):
        self.debug = False
        self.mode = None
        self.protocol = None
        self.screen_share_protocol = None
        self._handlers = {}
        self._listeners = []
        self._delisteners = []
        self.host = self.get_host()
        self.port = 5005
        self.screen_share_port = 5006
        self.running = False
        self.pass_code = None
        self.authenticated = False
        self.auth_handler = AuthHandler(self)
        self.screen_share_handler = ScreenShareHandler(self)
        self.file_handler = FileHandler(self)

    def setMode(self, mode):
        if mode == "server" or mode == "client":
            self.mode = mode
        else:
            raise Exception(f"Invalid mode: {mode}")

    def addHandler(self, event_name, fn):
        self._handlers[event_name] = fn

    def useHandler(self, event_name, *args):
        self._handlers[event_name](*args)

    def getHandlerNames(self):
        return self._handlers.keys()

    def addListener(self, listener):
        self._listeners.append(listener)

    def addDelistener(self, delistener):
        self._delisteners.append(delistener)

    def listen(self):
        for listener in self._listeners:
            reactor.callInThread(listener)

    def startGUI(self, gui):
        tksupport.install(gui.server_root if self.mode == "server" else gui.client_root)

    def send(self, event, *args):
        MAX_MSG_SIZE = 1024  # Assuming MAX_MSG_SIZE is defined elsewhere

        data = dumps({"event": event, "args": args})
        if len(data) <= MAX_MSG_SIZE:
            # Message fits within limit, send directly
            prefix = f"##HEAD{event:<10}{0:<4}{1:<4}##"
            msg = prefix.encode() + data + b"##FRAMEEND##"
            self.protocol.transport.write(msg)
        else:
            # Message exceeds limit, fragment and send
            num_chunks = (len(data) // MAX_MSG_SIZE) + 1  # Calculate number of chunks
            for chunk_num in range(num_chunks):
                start = chunk_num * MAX_MSG_SIZE
                end = min(start + MAX_MSG_SIZE, len(data))
                chunk = data[start:end]

                # Prefix with event name and chunk number for reassembly
                prefix = f"##HEAD{event:<10}{chunk_num:<4}{num_chunks:<4}##"
                msg = prefix.encode() + chunk + b"##FRAMEEND##"
                self.protocol.transport.write(msg)

    def start(self):
        self.running = True
        if self.mode == "server":
            mouse_keyboard_handler = MouseKeyboardHandler()
            self.addHandler("MOUSE", mouse_keyboard_handler.mouse)
            self.addHandler("KEYBOARD", mouse_keyboard_handler.keyboard)
            self.addHandler("FILE", self.file_handler.receive_file)
            self.addListener(self.screen_share_handler.capture_and_send)

            endpoint = TCP4ServerEndpoint(reactor, self.port)
            endpoint.listen(TCPFactory(self))
            screen_share_endpoint = TCP4ServerEndpoint(reactor, self.screen_share_port)
            screen_share_endpoint.listen(TCPFactory(self, True))
            if self.debug:
                print("DEBUG: Started TCP Server")
        elif self.mode == "client":
            inputhandling = InputHandling(self)
            self.addListener(inputhandling.start)
            self.addDelistener(inputhandling.stopListening)
            self.addHandler("SCREEN", self.screen_share_handler.receive)

            endpoint = TCP4ClientEndpoint(reactor, self.host, self.port)
            endpoint.connect(TCPFactory(self))
            screen_share_endpoint = TCP4ClientEndpoint(reactor, self.host, self.screen_share_port)
            screen_share_endpoint.connect(TCPFactory(self, True))
            if self.debug:
                print("DEBUG: Started TCP Client")
        else:
            raise Exception(f"Invalid mode: {self.mode}")

        self.listen()
        reactor.run()

    def stop(self):
        if self.running:
            for delistener in self._delisteners:
                delistener()
            reactor.getThreadPool().stop()
            self.protocol.transport.loseConnection()
            self.screen_share_protocol.transport.loseConnection()
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
