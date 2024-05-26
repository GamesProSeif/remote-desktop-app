import socket
from twisted.internet.protocol import Protocol, connectionDone, Factory
from pickle import loads, UnpicklingError
from io import BytesIO


class TCPProtocol(Protocol):
    def __init__(self, app, is_screen_share = False):
        self.app = app
        self.is_screen_share = is_screen_share
        if is_screen_share:
            self.app.screen_share_protocol = self
        else:
            self.app.protocol = self
        self.buffer = {}
        self.buffer["MAIN"] = BytesIO()
        for key in self.app.getHandlerNames():
            self.buffer[key] = BytesIO()

    def connectionMade(self):
        if self.app.debug:
            print("DEBUG: NEW_CONNECTION -", "SCREEN" if self.is_screen_share else "MAIN")

    def dataReceived(self, data: bytes):
        print("HEAD:", data[:40])
        try:
            # if data.decode() == self.app.pass_code:
            if data.decode() == "stop_screen_share":
                self.app.screen_share_handler.active = False
            elif self.app.auth_handler.check_pass_code(data.decode()):
                return self.transport.write("ok".encode())
            else:
                raise Exception()
        except Exception:
            try:
                self.buffer.write(data)
                if self.buffer.getvalue().find(b"stop_share_screen") != -1:
                    print("FOUND_HERE", self.buffer.getvalue().find(b"stop_share_screen"))
                delimiter_index = self.buffer.getvalue().find(b"##FRAMEEND##")
                print("rec:" ,len(self.buffer.getvalue()), delimiter_index)
                if delimiter_index != -1:
                    msg = loads(self.buffer.getvalue()[:delimiter_index])
                    event = msg["event"]
                    args = msg["args"]
                    self.app.useHandler(event, *args)

                    if self.app.debug:
                        if len(self.buffer.getvalue()) < 1000:
                            print(f"DEBUG: RECEIVED {event} - {msg}")
                        else:
                            print(f"DEBUG: RECEIVED {event} - too long to show")

                    self.buffer = BytesIO(self.buffer.getvalue()[delimiter_index + len(b"##FRAMEEND##"):])
            except Exception as exception:
                if self.is_screen_share:
                    self.buffer = BytesIO(self.buffer.getvalue()[delimiter_index + len(b"##FRAMEEND##"):])
                    # self.buffer.seek(0)
                    # self.buffer.truncate()
                else:
                    raise exception

    def connectionLost(self, reason=connectionDone):
        if self.app.debug:
            print(f"DEBUG: CONNECTION_LOST - { 'SCREEN' if self.is_screen_share else 'MAIN '} - {reason.value}")


class TCPFactory(Factory):
    def __init__(self, app, is_screen_share = False):
        self.app = app
        self.is_screen_share = is_screen_share

    def buildProtocol(self, addr):
        return TCPProtocol(self.app, self.is_screen_share)

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
