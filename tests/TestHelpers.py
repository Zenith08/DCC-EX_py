import socket
import threading

from typing import Optional

from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Sensors import Sensor


class MockDCCEX(DCCEX):
    def __init__(self) -> None:
        super().__init__("192.168.4.1", 2560, True)
        #: The most recent command received by this mock object.
        self.last_command_received: str = ""

    def _init_sockets(self, ip: str, port: int) -> None:
        print(f"Would have created DCC-EX with ip: {ip} and port {port}.")

    def send_command(self, command: str) -> None:
        self.last_command_received = command


# ChatGPT code
class MockTCPServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888) -> None:
        self.host: str = host
        self.port: int = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.running: bool = False

        self.last_received: str = ""

    def start(self) -> None:
        # Initialize the server socket and bind it
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True

        # Thread to handle the client connection
        def handle_client() -> None:
            assert self.server_socket is not None  # Ensure server_socket is initialized
            self.client_socket, _ = self.server_socket.accept()
            self.client_socket.settimeout(1)
            while self.running:
                try:
                    data: bytes = self.client_socket.recv(1024)
                    if not data:
                        break
                    self.last_received = data.decode()
                except socket.timeout:
                    pass

            self.client_socket.close()

        threading.Thread(target=handle_client, daemon=True).start()

    def send(self, data: str):
        if self.client_socket is not None:
            self.client_socket.send(data.encode())

    def stop(self) -> None:
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()


class MockSensor(Sensor):
    def __init__(self):
        super().__init__(-1, -1, False)
    
    def manual_set_state(self, state: bool):
        self._set_state(state)
