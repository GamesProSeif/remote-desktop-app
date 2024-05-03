from pickle import dumps
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from structures.protocol import TCPFactory

host = "localhost"
port = 5005


class App:
    def __init__(self):
        self.debug = False
        self.mode = None
        self.protocol = None
        self._handlers = {}
        self._listeners = []

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

    def send(self, event, *args):
        msg = dumps({"event": event, "args": args})
        self.protocol.transport.write(msg)

    def start(self):
        if self.mode == "server":
            endpoint = TCP4ServerEndpoint(reactor, port)
            endpoint.listen(TCPFactory(self))
        elif self.mode == "client":
            endpoint = TCP4ClientEndpoint(reactor, host, port)
            endpoint.connect(TCPFactory(self))
        else:
            raise Exception(f"Invalid mode: {self.mode}")

        self.listen()
        reactor.run()
