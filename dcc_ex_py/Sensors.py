from typing import Any, Optional

from .Helpers import DecodedCommand


class Sensor:
    """Represents a single sensor that can be monitored."""

    def __init__(self, id: int, pin: int, inverted: bool) -> None:
        """Instantiates a Sensor when we first learn about it either because we created it or the command station told us about it.
        If we don't know this information at creation time, temporary values will be used and they will be filled in later.

        :param id: The internal id of this sensor.
        :param pin: The digital pin on the arduino used by this sensor.
        :param inverted: Whether the sensor has been digitally inverted by the command station or not.
        """
        self.id: int = id
        self.pin: int = pin
        self.inverted: bool = inverted
        self.active: bool = False

    def _pin_and_inverted_later(self, pin: int, inverted: bool) -> None:
        """An internal initialization function triggered when we don't know all of the information about this pin on instantiation.

        :param pin: The digital pin on the Arduino used by this sensor.
        :param inverted: Whether the sensor has been digitally inverted by the command station or not.
        """
        self.pin = pin
        self.inverted = inverted

    def _set_state(self, active: bool) -> None:
        """An internal notification when we recieve notice the pin state has changed from the command station.

        :param active: Whether the sensor is currently detecting a train or not.
        """
        self.active = active


class Sensors:
    """Wraps control of DCC-EX Sensors and handles inputs received from them.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller
        self.sensors: dict[int, Sensor] = {}

        self.controller.add_command_listener(self._command_received)

    def define_sensor(self, id: int, pin: int, inverted: bool) -> None:
        """Defines a new sensor with the command station based on the given information.

        :param id: The internal id of the sensor.
        :param pin: The digital pin on the Arduino used by this sensor.
        :param inverted: Whether the sensor is digitally inverted or not.
        """
        pullup: str = "0"
        if inverted:
            pullup = "1"

        self.controller.send_command(f"<S {id} {pin} {pullup}>")

    def delete_sensor(self, id: int) -> None:
        """Requests a sensor be deleted from the command station.

        :param id: The id of the sensor to delete.
        """
        self.controller.send_command(f"<S {id}>")

        if id in self.sensors:
            self.sensors.pop(id, None)

    def has_sensor(self, id: int) -> bool:
        """Checks if we have local knowledge of the given sensor.

        :param id: The id of the sensor to check for.

        :returns: True if the sensor is known about locally, false otherwise.
        """
        return id in self.sensors

    def get_sensor(self, id: int) -> Optional[Sensor]:
        """Returns the local representation of the target sensor, or None if it doesn't exist.

        :param id: The id of the sensor to get.
        :returns: The local sensor if present, None otherwise.
        """
        return self.sensors.get(id, None)

    def refresh_sensors(self) -> None:
        """Asks the command station to inform us of all currently connected sensors and their states.
        """
        self.controller.send_command("<Q>")

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        if command.command == 'Q':
            id: int = int(command.args[0])
            if len(command.args) == 3:  # New define
                inverted: bool = False
                if command.args[2] == "1":
                    inverted = True

                if id not in self.sensors:
                    self.sensors[id] = Sensor(id, int(command.args[1]), inverted)
                else:
                    self.sensors[id]._pin_and_inverted_later(int(command.args[1]), inverted)
            elif len(command.args) == 1:  # State update
                if id not in self.sensors:
                    self.sensors[id] = Sensor(id, 0, False)
                self.sensors[id]._set_state(True)
        elif command.command == 'q':
            id: int = int(command.args[0])
            if id not in self.sensors:
                self.sensors[id] = Sensor(id, 0, False)

            self.sensors[id]._set_state(False)
