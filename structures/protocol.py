from twisted.internet.protocol import Protocol, connectionDone, Factory
from pickle import loads


class TCPProtocol(Protocol):
    def __init__(self, app):
        self.app = app
        self.app.protocol = self

    def connectionMade(self):
        if self.app.debug:
            print("DEBUG: NEW_CONNECTION")

    def dataReceived(self, data: bytes):
        msg = loads(data)
        event = msg["event"]
        args = msg["args"]
        self.app.useHandler(event, *args)

        if self.app.debug:
            print(f"DEBUG: RECEIVED - {msg}")

    def connectionLost(self, reason=connectionDone):
        if self.app.debug:
            print(f"DEBUG: CONNECTION_LOST - {reason}")


class TCPFactory(Factory):
    def __init__(self, app):
        self.app = app

    def buildProtocol(self, addr):
        return TCPProtocol(self.app)
