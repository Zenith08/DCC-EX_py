import socket
import threading

from typing import Callable, List

from .Helpers import DecodedCommand
from .TrackPower import TrackPower
from .TrainEngines import TrainEngines
from .AccessoryDecoders import Accessories
from .Turnouts import Turnouts
from .Sensors import Sensors
from .DigitalOutputs import DigitalOutputs
from .Memory import Memory


class DCCEX:
    """Defines a connection to a DCC-EX server and provides interfaces for interacting with the different capabilities supported by the hardware.
    """

    def __init__(self, ip: str, port: int) -> None:
        """Create a new connection to a DCC-EX Server

        :param ip: The (local) ip address of the server to connect to. If you haven't set this, it is probably '192.168.4.1'
        :type ip: str
        :param port: The numeric port to connect on, usually 2560.
        :type port: int
        """
        # Internal prep
        self._init_sockets(ip, port)
        self.onPacketReceived: List[Callable[[DecodedCommand], None]] = []

        # Wrappers for extra functionality
        self.track_power: TrackPower = TrackPower(self)
        self.train_engines: TrainEngines = TrainEngines(self)
        self.accessories: Accessories = Accessories(self)
        self.turnouts: Turnouts = Turnouts(self)
        self.sensors: Sensors = Sensors(self)
        self.gpio: DigitalOutputs = DigitalOutputs(self)
        self.memory: Memory = Memory(self)

    def _listener(self) -> None:
        """Internal function where a listener thread waits to recieve messages from the server.
        """
        while True:
            message: bytes = self.client_socket.recv(1024)
            decodedMsg: DecodedCommand = DecodedCommand(message)

            for listener in self.onPacketReceived:
                listener(decodedMsg)

    def _init_listener(self) -> None:
        self.listener_thread: threading.Thread = threading.Thread(target=self._listener, daemon=True)
        self.listener_thread.start()

    def _init_sockets(self, ip: str, port: int) -> None:
        self.ip: str = ip
        self.port: int = port

        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))

    def send_command(self, command: str) -> None:
        command += '\n'
        self.client_socket.sendall(command.encode())

    def add_command_listener(self, callback: Callable[[DecodedCommand], None]) -> None:
        self.onPacketReceived.append(callback)

    def remove_command_listener(self, callback: Callable[[DecodedCommand], None]) -> None:
        self.onPacketReceived.remove(callback)
