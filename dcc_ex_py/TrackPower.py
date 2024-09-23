from typing import Any
from .Helpers import ActiveState, DecodedCommand, Track

class TrackPower:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.mainOn: bool = False
        self.progOn: bool = False
        self.currentMain: float = 0
        self.currentMax: float = 0
        self.currentTrip: float = 0

        self.controller.add_command_listener(self.command_received)

    def power_all_tracks(self, power: ActiveState) -> None:
        self.controller.send_command(f"<{power}>")
    
    def power_select_track(self, power: ActiveState, track: Track) -> None:
        self.controller.send_command(f"<{power} {track}>")
    
    def command_received(self, command: DecodedCommand) -> None:
        if command.command.startswith('p'):
            on: bool = False
            if command.command[1] == '1':
                on = True

            if len(command.args) == 1 and command.args[0] == "MAIN":
                self.mainOn = on
            elif len(command.args) == 1 and command.args[0] == "PROG":
                self.progOn = on
            else: # len(command.args == 0) or command.args[0] == "JOIN" either way set both of them.
                self.mainOn = on
                self.progOn = on
        
        elif command.command == 'c':
            self.currentMain = float(command.args[1])
            self.currentMax = float(command.args[5])
            self.currentTrip = float(command.args[7])
