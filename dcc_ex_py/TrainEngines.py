"""A module containing the TrainEngines helper class and the TrainEngine representation."""
from typing import Any
from .Helpers import DecodedCommand, Direction, ActiveState


class TrainEngine:
    """Represents an engine currently active on the track that the command station knows about.
    """

    def __init__(self, trainEngines: Any, cab: int) -> None:
        """## Internal Function, creating a new Train Engine has no meaning if called outside of the API.
        Instantiates a Train Engine when we first learn about it because the command station told us about it.

        Train Engines are not created when we first define them and are only created by broadcasts from the command staiton.

        :param trainEngines: The local TrainEngines that owns this train. Used for sending commands out from this object.
        :param cab: The DCC address of this locomotive (Locomotive and Accessory addresses are independent).
        """

        self.trainEngines: TrainEngines = trainEngines
        """An internal reference to our own controls so they can be controlled from this local instance."""
        self.cab: int = cab
        """The id of the train engine being controlled."""
        self.speed: int = 0
        """The speed of the engine without direction (0 - 126)."""
        self.direction: Direction = Direction.FORWARD
        """The direction of the engine."""

        self.functions: int = 0
        """An int where each bit represents a given function and whether it is on or off. Parse with get_function"""

    def get_function(self, function: int) -> ActiveState:
        """Checks if a given function is active or not on the locomotive.

        :param function: The function on the train to check (0-31).

        :returns: ActiveState.ON if the given function is active, otherwise ActiveState.OFF
        """
        if (self.functions >> function) & 0b1:
            return ActiveState.ON
        else:
            return ActiveState.OFF

    def _information_received(self, speedDir: int, func: int) -> None:
        """An internal notificaiton to update the train engine information based on information received from the broadcast.

        :param speed: The speed of the engine where bits 0-6 are speed from 1-128 and bit 7 is direction.
        :param func: The bit pattern for activated functions."""
        self.speed = speedDir & 0b1111111

        if speedDir & 0b10000000 != 0:
            self.direction = Direction.FORWARD
        else:
            self.direction = Direction.REVERSED

        self.functions = func

    def set_speed(self, speed: int, direction: Direction) -> None:
        """Sets the train engine's speed and direction. Does not update the local values, they are only updated from broadcasts.

        :param speed: The new speed to set the train to (0-126), -1 is emergency stop.
        :param direction: The direction to move the train in.
        """
        self.trainEngines.set_speed(self.cab, speed, direction)

    def set_function(self, function: int, active: ActiveState) -> None:
        """Sets the target function on or off for this train. Does not update the local value, they are only updated from broadcasts.

        :param function: The function to adjust (0-31).
        :param active: Whether to turn the function on or off. You must manually turn off functions that should not be latched.
        """
        self.trainEngines.set_cab_function(self.cab, function, active)


class TrainEngines:
    """Wraps control of DCC-EX Cab Control and handles feedback.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.engines: dict[int, TrainEngine] = {}
        """An internal mapping of cab ids to engines that can be controlled."""

        self.maxEngines: int = 0  # init unknown
        """The max number of engines the command station supports at the same time based on onboard memory (0 if not checked, doesn't include power limitations)."""

        self.controller.add_command_listener(self._command_received)

    def set_speed(self, cab: int, speed: int, direction: Direction) -> None:
        """Sets the speed of a target train engine in a given direction.

        :param cab: The DCC address of the train to control.
        :param speed: The speed to set the train to (0-126), -1 is emergency stop.
        :param direction: Whether the train should go forwards or backwards.
        """
        self.controller.send_command(f"<t 1 {cab} {speed} {direction}>")

    def forget_loco(self, cab: int) -> None:
        """Asks the command station to forget about the target locomotive. The command station will stop sending speed information for this train.

        :param cab: The DCC address of the train to forget about.
        """
        self.controller.send_command(f"<- {cab}>")

    def forget_all_locos(self) -> None:
        """Deletes all locomotives from the command station.
        """
        self.controller.send_command("<->")

    def check_max_engines(self) -> None:
        """Refreshes the information on how many locomotives the command station supports.
        The information will not be available right away, it comes from the return value from the server.
        """
        self.controller.send_command("<#>")

    def emergency_stop(self) -> None:
        """Emergency stops all trains, leaves track power on.
        """
        self.controller.send_command("<!>")

    def set_cab_function(self, cab: int, function: int, on: ActiveState) -> None:
        """Sets a given function on a train to on or off.

        :param cab: The DCC address of the target train.
        :param function: The function on the decoder to set (0-28).
        :param on: Whether to set the given function on or off.
        """
        self.controller.send_command(f"<F {cab} {function} {on}>")

    def get_engine(self, cab: int) -> TrainEngine:
        """Gets the local representation of the target train engine if one exists.
        If it does not exist, creates one and sets it up to have its details filled in later.

        :param cab: The DCC address of the target train.
        :returns: The local representation of the train engine at the given address.
        """
        if cab not in self.engines:
            self.engines[cab] = TrainEngine(self, cab)

        return self.engines[cab]

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        Note we discard T commands because they don't provide information on which loco they affect.

        :param command: The command we received after parsing it into a helper class.
        """
        if command.command == 'l':
            cab: int = int(command.args[0])
            engine: TrainEngine = self.engines.get(cab, TrainEngine(self, cab))
            if cab not in self.engines:
                self.engines[cab] = engine
            engine._information_received(int(command.args[2]), int(command.args[3]))
        elif command.command == '#':
            self.maxEngines = int(command.args[0])
