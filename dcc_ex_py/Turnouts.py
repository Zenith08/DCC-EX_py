"""A module containing the Turnouts helper class and Turnout representation."""
from typing import Any

from .Helpers import DecodedCommand, TurnoutControl, TurnoutProfiles, TurnoutState


class Turnout:
    """Represents a locally cached turnout and its properties.
    """

    def __init__(self, turnouts: Any, id: int) -> None:
        """Instantiates a turnout at the point we do not have any information on it. Sets everything to temp values to fill in later.

        :param id: The id of the turnout to use.
        """

        self.turnouts: Turnouts = turnouts
        """An internal reference to our own turnouts so we can send commands from this object."""
        self.id: int = id
        """The id of this turnout."""
        self.controlType: TurnoutControl = TurnoutControl.LCN  # placeholder since it's the least common one.
        """The method being used to control this turnout (Defaults to LCN until we are told otherwise.)"""
        self.thrown: TurnoutState = TurnoutState.CLOSED
        """The state the turnout is currently in (Initializes to Closed)."""

        # DCC Only
        self.address: int = 0
        """The primary DCC address for this turnout if it using DCC control (default 0)."""
        self.subaddress: int = 0
        """The DCC subaddress for this turnout if it is using DCC control."""

        # VPin or Servo
        self.pin: int = 0
        """The digital output pin used by this turnout if it is being controled either by a servo or digital pin."""

        # Servo only
        self.thrown_position: int = 0
        """The pwm rate to use for the thrown position if this turnout is being controlled by a servo."""
        self.closed_position: int = 0
        """The pwm rate to use for the closed position if this turnout is being controlled by a servo."""
        self.profile: TurnoutProfiles = TurnoutProfiles.IMMEDIATE  # placeholder
        """The rate at which this turnout changes state if this turnout is being controlled by a servo."""

    def _setup_dcc(self, address: int, subaddress: int) -> None:
        """An internal initialization function to add DCC information we learn after instantiation.

        :param address: The primary DCC address of this turnout.
        :param subaddress: The subaddress for this turnout on it's decoder.
        """
        self.controlType = TurnoutControl.DCC
        self.address = address
        self.subaddress = subaddress

    def _setup_servo(self, pin: int, thrown_position: int, closed_position: int, profile: TurnoutProfiles) -> None:
        """An internal initialization function to add servo information we learn after instantiation.

        :param pin: The digital pin used by this turnout.
        :param thrown_position: The PWM frequency to use when the turnout is thrown.
        :param closed_position: The PWM frequency to use when the turnout is closed.
        :param profile: Defines how quickly the turnout should be instructed to switch from one state to the other.
        """
        self.controlType = TurnoutControl.SERVO
        self.pin = pin
        self.thrown_position = thrown_position
        self.closed_position = closed_position
        self.profile = profile

    def _setup_vpin(self, pin: int) -> None:
        """An internal initialization function to add digital pin information we learn after instantiation.

        :param pin: The digital pin used by this turnout.
        """
        self.controlType = TurnoutControl.PIN
        self.pin = pin

    def _setup_lcn(self) -> None:
        """An internal initialization function to identify this turnout as part of LCN.
        """
        self.controlType = TurnoutControl.LCN

    def _set_state(self, state: TurnoutState) -> None:
        """An internal notification when we recieve notice the pin state has changed from the command station.

        :param state: The updated state of this digital pin.
        """
        self.thrown = state

    def set_state(self, state: TurnoutState) -> None:
        """Requests that the turnout be set to the desired state.

        :param state: The state to set the turnout to.
        """
        # Of note, we don't update our local state here, that still comes from feedback from the server.
        self.turnouts.set_turnout(self.id, state)


class Turnouts:
    """Wraps control of DCC-EX Turnouts and handles feedback.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.turnouts: dict[int, Turnout] = {}

        self.controller.add_command_listener(self._command_received)

    def create_dcc_turnout(self, id: int, linear_address: int) -> Turnout:
        """Defines a turnout on the command station using a linear address DCC accessory decoder.

        :param id: The id of the turnout to create.
        :param linear_address: The linear address of the accessory decoder + channel combination to set.
        """
        self.controller.send_command(f"<T {id} DCC {linear_address}>")

        self.turnouts[id] = Turnout(self, id)
        return self.turnouts[id]

    def create_dcc_turnout_subaddress(self, id: int, address: int, subaddress: int) -> Turnout:
        """Defines a turnout on the command station using an address and subaddress DCC accessory decoder.

        :param id: The id of the turnout to create.
        :param address: The non-linear address of the accessory decoder + channel combination to set.
        :param subaddress: For accessory decoders with multiple functions, subaddress chooses the function within the decoder.
        """
        self.controller.send_command(f"<T {id} DCC {address} {subaddress}>")

        self.turnouts[id] = Turnout(self, id)
        return self.turnouts[id]

    def create_servo_turnout(self, id: int, pin: int, thrown_position: int, closed_position: int, profile: TurnoutProfiles) -> Turnout:
        """Defines a turnout on the command station controlled by a servo attached to a digital pin on the Arduino.

        :param id: The id of the turnout to create.
        :param pin: The digital pin on the Arduino this turnout uses.
        :param thrown_position: The PWM frequency to use when the turnout is thrown.
        :param closed_position: The PWM frequency to use when the turnout is closed.
        :param profile: Defines how quickly the turnout should be instructed to switch from one state to the other.
        """
        self.controller.send_command(f"<T {id} SERVO {pin} {thrown_position} {closed_position} {profile}>")

        self.turnouts[id] = Turnout(self, id)
        return self.turnouts[id]

    def create_gpio_turnout(self, id: int, pin: int) -> Turnout:
        """Defines a turnout on the command station controlled digitally by an output pin on the Arduino.

        :param id: The id of the turnout to create.
        :param pin: The digital pin on the Arduino this turnout uses.
        """
        self.controller.send_command(f"<T {id} VPIN {pin}>")

        self.turnouts[id] = Turnout(self, id)
        return self.turnouts[id]

    def delete_turnout(self, id: int) -> None:
        """Deletes a turnout on the command station.

        :param id: The id of the turnout to delete.
        """
        self.controller.send_command(f"<T {id}>")
        self.turnouts.pop(id, None)

    def refresh_turnouts(self) -> None:
        """Asks the command station to give us information on all defined turnouts.
        """
        self.controller.send_command("<T>")

    def set_turnout(self, id: int, state: TurnoutState) -> None:
        """Sets the turnout at the given id to a target state.

        :param id: The id of the turnout to set.
        :param state: Whether to set the turnout to closed (normal) or thrown (open/branch)."""
        self.controller.send_command(f"<T {id} {state}>")

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        if command.command == 'H':
            id: int = int(command.args[0])
            if id not in self.turnouts:
                self.turnouts[id] = Turnout(self, id)

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
