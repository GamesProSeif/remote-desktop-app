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
        # print("rec-size:", len(data))
        # print("HEAD:", data[:40])
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
                # print("PREVHEAD:", self.buffer["MAIN"].getvalue()[:40])
                self.buffer["MAIN"].seek(len(self.buffer["MAIN"].getvalue()))
                self.buffer["MAIN"].write(data)
                while True:
                    # print("HEAD:", self.buffer["MAIN"].getvalue()[:40])
                    start_index = self.buffer["MAIN"].getvalue().find(b"##HEAD")
                    end_index = self.buffer["MAIN"].getvalue().find(b"##FRAMEEND##")
                    if end_index == -1:
                        break
                    event_name = self.buffer["MAIN"].getvalue()[start_index+6:start_index+16].strip().decode()
                    chunk_num = int(self.buffer["MAIN"].getvalue()[start_index+16:start_index+20].strip())
                    chunk_max = int(self.buffer["MAIN"].getvalue()[start_index+20:start_index+24].strip())
                    encoded_data = self.buffer["MAIN"].getvalue()[start_index+26:end_index]
                    # print(event_name, "start:", start_index, "end:", end_index, "chunk_num:", chunk_num, "chunk_max:", chunk_max)
                    if start_index != 0:
                        raise Exception("startindex is not 0")
                    # print("rec:" ,len(self.buffer[event_name].getvalue()), delimiter_index)

                    self.buffer["MAIN"] = BytesIO(self.buffer["MAIN"].getvalue()[end_index + len(b"##FRAMEEND##"):])
                    # print("NEXT_HEAD:", self.buffer["MAIN"].getvalue()[:40])

                    self.buffer[event_name].write(encoded_data)

                    if chunk_num + 1 != chunk_max:
                        continue

                    msg = loads(self.buffer[event_name].getvalue())
                    event = msg["event"]
                    args = msg["args"]
                    self.app.useHandler(event, *args)

                    if self.app.debug:
                        if len(self.buffer[event_name].getvalue()) < 1000:
                            print(f"DEBUG: RECEIVED {event} - {msg}")
                        else:
                            print(f"DEBUG: RECEIVED {event} - too long to show")

                    self.buffer[event_name].seek(0)
                    self.buffer[event_name].truncate()

                # if self.buffer[event_name].getvalue().find(b"stop_share_screen") != -1:
                #     print("FOUND_HERE", self.buffer[event_name].getvalue().find(b"stop_share_screen"))
                # delimiter_index = self.buffer[event_name].getvalue().find(b"##FRAMEEND##")
                # print("rec:" ,len(self.buffer[event_name].getvalue()), delimiter_index)
                # if delimiter_index != -1:
                #     msg = loads(self.buffer[event_name].getvalue()[:delimiter_index])
                #     event = msg["event"]
                #     args = msg["args"]
                #     self.app.useHandler(event, *args)

                #     if self.app.debug:
                #         if len(self.buffer[event_name].getvalue()) < 1000:
                #             print(f"DEBUG: RECEIVED {event} - {msg}")
                #         else:
                #             print(f"DEBUG: RECEIVED {event} - too long to show")

                #     self.buffer[event_name] = BytesIO(self.buffer[event_name].getvalue()[delimiter_index + len(b"##FRAMEEND##"):])
            except Exception as exception:
                if self.is_screen_share:
                    # self.buffer["SCREEN"] = BytesIO(self.buffer["SCREEN"].getvalue()[delimiter_index + len(b"##FRAMEEND##"):])
                    self.buffer.seek(0)
                    self.buffer.truncate()
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
