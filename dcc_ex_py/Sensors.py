from typing import Any

from .Helpers import DecodedCommand

class Sensor:
    def __init__(self, id: int, pin: int, inverted: bool) -> None:
        self.id: int = id
        self.pin: int = pin
        self.inverted: bool = inverted
        self.active: bool = False
    
    def _pin_and_inverted_later(self, pin: int, inverted: bool) -> None:
        self.pin = pin
        self.inverted = inverted
    
    def _set_state(self, active: bool) -> None:
        self.active = active


class Sensors:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller
        self.sensors: dict[int, Sensor] = {}

        self.controller.add_command_listener(self.command_received)
    
    def define_sensor(self, id: int, pin: int, inverted: bool) -> None:
        pullup: str = "0"
        if inverted:
            pullup = "1"
        
        self.controller.send_command(f"<S {id} {pin} {pullup}>")
    
    def delete_sensor(self, id: int) -> None:
        self.controller.send_command(f"<S {id}>")

        if id in self.sensors:
            self.sensors.pop(id, None)
    
    def has_sensor(self, id: int) -> bool:
        return id in self.sensors

    def get_sensor(self, id: int) -> Sensor | None:
        return self.sensors.get(id, None)

    def refresh_sensors(self) -> None:
        self.controller.send_command("<Q>")
    
    def command_received(self, command: DecodedCommand) -> None:
        if command.command == 'Q':
            id: int = int(command.args[0])
            if len(command.args) == 3: # New define
                inverted: bool = False
                if command.args[2] == "1":
                    inverted = True

                if id not in self.sensors:
                    self.sensors[id] = Sensor(id, int(command.args[1]), inverted)
                else:
                    self.sensors[id]._pin_and_inverted_later(int(command.args[1]), inverted)
            elif len(command.args) == 1: # State update
                if id not in self.sensors:
                    self.sensors[id] = Sensor(id, 0, False)
                self.sensors[id]._set_state(True)
        elif command.command == 'q':
            id: int = int(command.args[0])
            if id not in self.sensors:
                self.sensors[id] = Sensor(id, 0, False)

            self.sensors[id]._set_state(False)
