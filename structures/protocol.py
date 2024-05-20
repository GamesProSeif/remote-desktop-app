import socket
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
        try:
            # if data.decode() == self.app.pass_code:
            if self.app.auth_handler.check_pass_code(data.decode()):
                return self.transport.write("ok".encode())
        except UnicodeDecodeError:
            msg = loads(data)
            event = msg["event"]
            args = msg["args"]
            self.app.useHandler(event, *args)

            if self.app.debug:
                print(f"DEBUG: RECEIVED - {msg}")

    def connectionLost(self, reason=connectionDone):
        if self.app.debug:
            print(f"DEBUG: CONNECTION_LOST - {reason.value}")


class TCPFactory(Factory):
    def __init__(self, app):
        self.app = app

    def buildProtocol(self, addr):
        return TCPProtocol(self.app)

def is_server_listening(host, port, code):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            sock.sendall(code.encode())
            res = sock.recv(1024).decode()
            return res.strip() == "ok"
        return False
    except socket.timeout:
        return False
    finally:
        sock.close()
