"""A module containing the TrackPower helper class."""
from typing import Any
from .Helpers import ActiveState, DecodedCommand, Track


class TrackPower:
    """Wraps control of DCC-EX Track Power and provides access to power usage diagnostics.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.mainOn: bool = False
        """The status of power to the Main track."""
        self.progOn: bool = False
        """The status of power to the programming track."""
        self.currentMain: float = 0
        """The most recent report of power draw from the main track (0 if not checked)."""
        self.currentMax: float = 0
        """The most recent report of the max power draw from the main track (0 if not checked)."""
        self.currentTrip: float = 0
        """The most recent report of circuit trip power draw (0 if not checked)."""

        self.controller.add_command_listener(self._command_received)

    def power_all_tracks(self, power: ActiveState) -> None:
        """Asks the command station to change the power of all tracks to the given power state.

        :param power: Whether to turn the main and programming tracks on or off.
        """
        self.controller.send_command(f"<{power}>")

    def power_select_track(self, power: ActiveState, track: Track) -> None:
        """Asks the command station to set the target tracks power to the given state.

        :param power: Whether to turn the track on or off.
        :param track: The track to set the power on, either: Main, Programming, or Both.
        """
        self.controller.send_command(f"<{power} {track}>")

    def refresh_power_information(self) -> None:
        """Asks the command station to tell us what power is being used on each track.
        """
        self.controller.send_command("<c>")

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        if command.command.startswith('p'):
            on: bool = False
            if command.command[1] == '1':
                on = True

            if len(command.args) == 1 and command.args[0] == "MAIN":
                self.mainOn = on
            elif len(command.args) == 1 and command.args[0] == "PROG":
                self.progOn = on
            else:  # len(command.args == 0) or command.args[0] == "JOIN" either way set both of them.
                self.mainOn = on
                self.progOn = on

        elif command.command == 'c':
            self.currentMain = float(command.args[1])
            self.currentMax = float(command.args[5])
            self.currentTrip = float(command.args[7])
