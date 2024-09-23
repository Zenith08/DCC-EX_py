from typing import Any

from .Helpers import ActiveState, DecodedCommand, IFlag

class DigitalOutputs:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.outputs: dict[int, DigitalOutput] = {}

        self.controller.add_command_listener(self.command_received)
    
    def create_output_pin(self, id: int, pin: int, flags: IFlag) -> None:
        self.controller.send_command(f"<Z {id} {pin} {str(flags)}>")

        self.outputs[id] = DigitalOutput(id, pin, flags)

    def delete_output_pin(self, id: int) -> None:
        self.controller.send_command(f"<Z {id}>")

        self.outputs.pop(id, None)

    def set_output_pin(self, id: int, state: ActiveState) -> None:
        self.controller.send_command(f"<Z {id} {state}>")
        # this auto causes a return, we update our local cache using that instead.

    def refresh_output_pins(self) -> None:
        self.controller.send_command("<Z>")
    
    def command_received(self, command: DecodedCommand) -> None:
        if command.command == 'Y':
            if command.args == 4: # Full definition
                id: int = int(command.args[0])
                if id not in self.outputs:
                    self.outputs[id] = DigitalOutput(id, int(command.args[1]), IFlag(int(command.args[2])))
                else:
                    self.outputs[id]._vpin_and_flag_later(int(command.args[1]), IFlag(int(command.args[2])))

                self.outputs[id]._set_state(ActiveState(command.args[3]))

            elif command.args == 2: # State update successful
                id: int = int(command.args[0])
                if id not in self.outputs:
                    self.outputs[id] = DigitalOutput(id, 0, IFlag.DEFAULT_ACTIVE)
                self.outputs[id]._set_state(ActiveState(command.args[1]))

class DigitalOutput:
    def __init__(self, id: int, vpin: int, iflag: IFlag) -> None:
        self.id: int = id
        self.vpin: int = vpin
        self.iflag: IFlag = iflag
        self.state: ActiveState = ActiveState.OFF
    
    # Happens when we first learn about this output because of a state change instead of a full definition
    def _vpin_and_flag_later(self, vpin: int, iflag: IFlag) -> None:
        self.vpin = vpin
        self.iflag = iflag
    
    def _set_state(self, state: ActiveState) -> None:
        self.state = state
