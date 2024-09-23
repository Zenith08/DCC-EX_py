from typing import Any

from .Helpers import DecodedCommand, TurnoutControl, TurnoutProfiles, TurnoutState


class Turnouts:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.turnouts: dict[int, Turnout] = {}

        self.controller.add_command_listener(self.command_received)

    def create_dcc_turnout(self, id: int, linear_address: int) -> None:
        self.controller.send_command(f"<T {id} DCC {linear_address}>")
    
    def create_dcc_turnout_sub(self, id: int, address: int, subaddress: int) -> None:
        self.controller.send_command(f"<T {id} DCC {address} {subaddress}>")
    
    def create_servo_turnout(self, id: int, pin: int, thrown_position: int, closed_position: int, profile: TurnoutProfiles) -> None:
        self.controller.send_command(f"<T {id} SERVO {pin} {thrown_position} {closed_position} {profile}>")

    def create_gpio_turnout(self, id: int, pin: int) -> None:
        self.controller.send_command(f"<T {id} VPIN {pin}>")
    
    def delete_turnout(self, id: int) -> None:
        self.controller.send_command(f"<T {id}>")
    
    def refresh_turnouts(self) -> None:
        self.controller.send_command(f"<T>")
    
    def set_turnout(self, id: int, state: TurnoutState) -> None:
        self.controller.send_command(f"<T {id} {state}>")

    def command_received(self, command: DecodedCommand) -> None:
        if command.command == 'H':
            id: int = int(command.args[0])
            if id not in self.turnouts:
                self.turnouts[id] = Turnout(id)

            if len(command.args) == 5:
                self.turnouts[id]._setup_dcc(int(command.args[2]), int(command.args[3]))
                self.turnouts[id]._set_state(TurnoutState(command.args[4]))
            elif len(command.args) == 7:
                self.turnouts[id]._setup_servo(int(command.args[2]), int(command.args[3]), int(command.args[4]), TurnoutProfiles(command.args[5]))
                self.turnouts[id]._set_state(TurnoutState(command.args[6]))
            elif len(command.args) == 4:
                self.turnouts[id]._setup_vpin(int(command.args[2]))
                self.turnouts[id]._set_state(TurnoutState(command.args[3]))
            elif len(command.args) == 3:
                self.turnouts[id]._setup_lcn()
                self.turnouts[id]._set_state(TurnoutState(command.args[2]))
            elif len(command.args) == 2:
                # Not defined but state changed
                self.turnouts[id]._set_state(TurnoutState(command.args[1]))

class Turnout:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.controlType: TurnoutControl = TurnoutControl.LCN # placeholder
        self.thrown: TurnoutState = TurnoutState.CLOSED
        # DCC only
        self.address: int = 0
        self.subaddress: int = 0
        # VPin or Servo
        self.vpin: int = 0
        # Servo only
        self.thrown_position: int = 0
        self.closed_position: int = 0
        self.profile: TurnoutProfiles = TurnoutProfiles.IMMEDIATE # placeholder

    def _setup_dcc(self, address: int, subaddress: int) -> None:
        self.controlType = TurnoutControl.DCC
        self.address = address
        self.subaddress = subaddress

    def _setup_vpin(self, pin: int) -> None:
        self.controlType = TurnoutControl.VPIN
        self.vpin = pin

    def _setup_servo(self, pin: int, thrown_pos: int, closed_pos: int, profile: TurnoutProfiles) -> None:
        self.controlType = TurnoutControl.SERVO
        self.vpin = pin
        self.thrown_position = thrown_pos
        self.closed_position = closed_pos
        self.profile = profile

    def _setup_lcn(self) -> None:
        self.controlType = TurnoutControl.LCN

    def _set_state(self, state: TurnoutState) -> None:
        self.thrown = state
