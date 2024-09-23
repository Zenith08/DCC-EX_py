from typing import Any

from .Helpers import DecodedCommand, TurnoutProfiles, TurnoutState

class Memory:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.nTurnoutsSaved: int = 0
        self.nSensorsSaved: int = 0
        self.nOutputsSaved: int = 0

        self.controller.add_command_listener(self.command_received)
    
    def save_eeprom(self) -> None:
        self.controller.send_command("<E>")
    
    def delete_eeprom(self) -> None:
        self.controller.send_command("<e>")

    def command_received(self, command: DecodedCommand) -> None:
        if command.command == 'e': # returned when save successful
            self.nTurnoutsSaved = int(command.args[0])
            self.nSensorsSaved = int(command.args[1])
            self.nOutputsSaved = int(command.args[2])

        elif command.command == '0': # returned when delete successful
            self.nTurnoutsSaved = 0
            self.nSensorsSaved = 0
            self.nOutputsSaved = 0
