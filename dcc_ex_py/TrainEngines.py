from typing import Any
from .Helpers import DecodedCommand, Direction, ActiveState

class TrainEngines:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.engines: list[ActiveEngine] = []
        self.maxEngines: int = 0 # init unknown

        self.controller.add_command_listener(self.command_received)

    def set_speed(self, cab: int, speed: int, direction: Direction) -> None:
        self.controller.send_command(f"<t 1 {cab} {speed} {direction}>")

    def forget_loco(self, cab: int) -> None:
        self.controller.send_command(f"<- {cab}>")
    
    def forget_all_locos(self) -> None:
        self.controller.send_command("<->")
    
    def emergency_stop(self) -> None:
        self.controller.send_command("<!>")

    def set_cab_function(self, cab: int, function: int, on: ActiveState) -> None:
        self.controller.send_command(f"<F {cab} {function} {on}>")

    def command_received(self, command: DecodedCommand) -> None:
        # TODO treat:
        # T
        # '#' command, also needs outbound function
        # 'l' (idk if this is new or old function system)
        pass

class ActiveEngine:
    def __init__(self, cab: int) -> None:
        self.cab: int = cab
        self.speed: int = 0
        self.forward: Direction = Direction.FORWARD

        # TODO functions don't seem to have a return value so the are ignored here