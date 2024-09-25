from typing import Any
from .Helpers import DecodedCommand, Direction, ActiveState


class TrainEngines:
    """Wraps control of DCC-EX Cab Control and handles feedback.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.engines: list[ActiveEngine] = []
        self.maxEngines: int = 0  # init unknown

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

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        # TODO treat:
        # T
        # '#' command, also needs outbound function
        # 'l' (idk if this is new or old function system)
        pass


class ActiveEngine:
    """Represents an engine currently active on the track that the command station knows about.
    TODO
    """

    def __init__(self, cab: int) -> None:
        self.cab: int = cab
        self.speed: int = 0
        self.forward: Direction = Direction.FORWARD

        # TODO functions don't seem to have a return value so the are ignored here
