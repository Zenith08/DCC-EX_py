"""A module containing the Memory helper class."""
from typing import Any

from .Helpers import DecodedCommand


class Memory:
    """Wraps control of DCC-EX Memory and feedback on saved information.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance
        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.nTurnoutsSaved: int = 0
        """The number of turnouts saved when the EEPROM was most recently saved. 0 if memory has not been saved."""
        self.nSensorsSaved: int = 0
        """The number of sensors saved when the EEPROM was most recently saved. 0 if memory has not been saved."""
        self.nOutputsSaved: int = 0
        """The number of digital outputs saved when the EEPROM was most recently saved. 0 if memory has not been saved."""

        self.controller.add_command_listener(self._command_received)

    def save_eeprom(self) -> None:
        """Requests the command station saves the created turnouts, sensors, and outputs to the EEPROM
        """
        self.controller.send_command("<E>")

    def delete_eeprom(self) -> None:
        """Requests the command station deletes the EEPROM memory.
        """
        self.controller.send_command("<e>")
        self.nTurnoutsSaved = 0
        self.nSensorsSaved = 0
        self.nOutputsSaved = 0

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        if command.command == 'e':  # returned when save successful
            self.nTurnoutsSaved = int(command.args[0])
            self.nSensorsSaved = int(command.args[1])
            self.nOutputsSaved = int(command.args[2])
        elif command.command == '0':  # returned when delete successful
            self.nTurnoutsSaved = 0
            self.nSensorsSaved = 0
            self.nOutputsSaved = 0
