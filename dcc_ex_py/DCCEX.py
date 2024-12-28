"""A module containing the DCCEX object which allows connections to a DCC-EX Server."""
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
from .CVProgrammer import CVProgrammer


class DCCEX:
    """Defines a connection to a DCC-EX server and provides interfaces for interacting with the different capabilities supported by the hardware.
    """

    def __init__(self, ip: str, port: int, testMode: bool = False) -> None:
        """Create a new connection to a DCC-EX Server

        :param ip: The (local) ip address of the server to connect to. If you haven't set this, it is probably '192.168.4.1'
        :param port: The numeric port to connect on, usually 2560.
        :param testMode: Used by the PyTest system to disable networking. Should be set to False for normal operation.
        """
        self.ip: str = ip
        """The ip address of the DCC-EX server this instance is connected to."""
        self.port: int = port
        """The port of the DCC-EX server this instance is connected to."""

        # Internal prep
        self._onPacketReceived: List[Callable[[DecodedCommand], None]] = []
        self._listener_running = False
        if not testMode:
            self._init_sockets()
            self._init_listener()

        # Wrappers for extra functionality
        self.track_power: TrackPower = TrackPower(self)
        """Wrapper for track power commands."""
        self.train_engines: TrainEngines = TrainEngines(self)
        """Wrapper for train engine commands."""
        self.accessories: Accessories = Accessories(self)
        """Wrapper for accessory decoder commands."""
        self.turnouts: Turnouts = Turnouts(self)
        """Wrapper for turnout commands."""
        self.sensors: Sensors = Sensors(self)
        """Wrapper for sensor commands."""
        self.digitalOutputs: DigitalOutputs = DigitalOutputs(self)
        """Wrapper for digital output commands."""
        self.memory: Memory = Memory(self)
        """Wrapper for memory commands."""
        self.programming: CVProgrammer = CVProgrammer(self)
        """Wrapper for CV programming commands."""

    def _listener(self) -> None:
        """Internal function where a listener thread waits to recieve messages from the server.
        """
        self._listener_running = True
        self._client_socket.settimeout(1.0)
        while self._listener_running:
            try:
                message: bytes = self._client_socket.recv(1024)
                decodedMsg: DecodedCommand = DecodedCommand(message)

                for listener in self._onPacketReceived:
                    listener(decodedMsg)
            except socket.timeout:
                pass

    def _init_listener(self) -> None:
        """Internal function to start the listener thread.
        """
        self._listener_thread: threading.Thread = threading.Thread(target=self._listener, daemon=True)
        self._listener_thread.start()

    def _init_sockets(self) -> None:
        """Internal function to create socket objects and connect to the server.
        """
        self._client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.connect((self.ip, self.port))

    def send_command(self, command: str) -> None:
        """Send a string command to the DCC-EX Controller. Note that the command is not validated, a newline is added to the end of it though.
        For pre-formatted commands, consider using one of the available helper classes instead.

        :param command: The string command to be sent to DCC-EX
        """
        command += '\n'
        self._client_socket.sendall(command.encode())

    def add_command_listener(self, callback: Callable[[DecodedCommand], None]) -> None:
        """Register a callback function to be called if we receive input from the DCC-EX Controller.

        :param callback: The function to be called, it is passed a DecodedCommand which contains all the relavent information. It is not required to return anything.
        """
        self._onPacketReceived.append(callback)

    def remove_command_listener(self, callback: Callable[[DecodedCommand], None]) -> None:
        """Remove a callback function from the list of callbacks called when a packet is received.

        :param callback: The callback function to remove.
        """
        self._onPacketReceived.remove(callback)

    def quit(self) -> None:
        """Gracefully shut down the connection to DCC-EX by stopping the listener thread and closing the socket.
        """
        self._listener_running = False
        self._listener_thread.join()
        self._client_socket.close()
