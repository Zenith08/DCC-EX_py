"""Provides access to CV programming functionality of DCC-EX including DCC addresses.
Due to the different situation this is used in cmopared to train operations, callbacks are enabled for feedback from each command.
Callbacks come from the DCC-EX listener thread, while you are using it for work no messages will be processed from the command station.
"""

from typing import Any, Callable

from dcc_ex_py.Helpers import ActiveState, DecodedCommand


class ExpectedCallback:
    """Internal representation of a query that has been sent to the programming track and is expecting a callback.
    All arguments are converted to ints before being sent.

    :param expectedCmd: The character at the start of the response we are expecting. Other responses will be ignored.
    :param callback: The callback command to invoke.
    """
    def __init__(self, expectedCmd: str, expectedArgs: int, callback: Callable[..., None]) -> None:
        self.cmdKey: str = expectedCmd
        """The first letter indicating the response we are expecting."""
        self.expectedArgs: int = expectedArgs
        """The number of arguments expected to be received from the query."""
        self.callback: Callable[..., None] = callback
        """The callback that will be invoked when the response is retrieved."""

    def _response_received(self, response: DecodedCommand) -> bool:
        """Called when a given command is received, invokes the callback assigned.
        Arguments converted to ints before being passed to the function.

        :param response: The full command that has been received.

        :return: True if this callback consumes the command.
        """
        if self.cmdKey == response.command and self.expectedArgs == len(response.args) and self.callback is not None:
            args: list[int] = [int(item) for item in response.args]

            # Python thing, the list is passed as the arguments instead of as a list[str]
            self.callback(*args)
            return True
        else:
            return False


class CVProgrammer:
    """Wraps the CV programming functionality of the DCC-EX system.
    All callbacks come from the DCC-EX listener thread, while you are using it for work no messages will be processed from the command station.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance.

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

        self.controller.add_command_listener(self._command_received)
        self._awaitingCallbacks: list[ExpectedCallback] = []

    def write_cv_bit_main(self, cab: int, cv: int, bit: int, value: ActiveState) -> None:
        """Writes a single bit of the specified CV of the specified locomotive on the main track.

        :param cab: The DCC address of the train to target.
        :param cv: The configuration value on the locomotive to write (0-1024).
        :param bit: The individual bit to write (0-7).
        :param value: Whether the target bit should be ON (1) or OFF (0)
        """
        self.controller.send_command(f"<b {cab} {cv} {bit} {value}>")

    def write_cv_main(self, cab: int, cv: int, value: int) -> None:
        """Writes a value to the specified CV of the target locomotive on the main track.

        :param cab: The DCC address of the train to target.
        :param cv: The configuration value on the locomotive to write (1-1024).
        :param value: The value to write to the CV (0-255).
        """
        self.controller.send_command(f"<w {cab} {cv} {value}>")

    def read_cv(self, cv: int, callback: Callable[[int, int], None]) -> None:
        """Reads a target cv on the programming track. (Only 1 loco can be on the programming track.)
        Use read_dcc_address to read a locomotives address.

        :param cv: The CV to read (1-1024).
        :param callback: A function to be called with the read CV value. Arguments are (cv, value), Value -1 indicates a failure.
        """
        self.controller.send_command(f"<R {cv}>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("v", 2, callback))

    def read_dcc_address(self, callback: Callable[[int], None]) -> None:
        """Read the DCC address in use by the locomotive. DCC-EX automatically reads the long or short address as needed.

        :param callback: A function to be called with the read DCC address. Arguments are (address), -1 is a failure.
        """
        self.controller.send_command("<R>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("r", 1, callback))

    def verify_cv_bit(self, cv: int, bit: int, expected: ActiveState, callback: Callable[[int, int, int], None]) -> None:
        """DCC-EX tests the specified bit of a cv value against the expected value and returns the true value of the CV.
        Runs faster if the CV matches the expected value.

        :param cv: The CV to check against (1-1024).
        :param bit: The individual bit to check (0-7, 0 is least significant).
        :param expected: Whether we expect the bit to be 1 (ON) or 0 (OFF).
        :param callback: A function to be called with the read CV value. Arguments are (cv, bit, value), -1 is a failure.
        """
        self.controller.send_command(f"<V {cv} {bit} {expected}>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("v", 3, callback))

    def verify_cv(self, cv: int, expected: int, callback: Callable[[int, int], None]) -> None:
        """DCC-EX tests the specified cv value against the expected value and returns the true value of the CV.
        Runs faster if the CV matches the expected value.

        :param cv: The CV to check against (1-1024).
        :param expected: The expected value of the CV in question (0-255).
        :param callback: A function to be called with the read CV value. Arguments are (cv, value), -1 is a failure.
        """
        self.controller.send_command(f"<V {cv} {expected}>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("v", 2, callback))

    def write_cv_bit(self, cv: int, bit: int, state: ActiveState) -> None:
        """Writes the target bit of the target CV on the programming track.
        The response for this callback is undocumented and as such no callbacks are provided.

        :param cv: The CV to write to (1-1024).
        :param bit: The individual bit to write (0-7).
        :param state: Whether to set the target bit ON (1) or OFF (0)
        """
        self.controller.send_command(f"<B {cv} {bit} {state}>")

    def write_cv(self, cv: int, value: int, callback: Callable[[int, int], None]) -> None:
        """Writes the value to the target CV on the programming track.

        :param cv: The CV to write to (1-1024).
        :param value: The value to write to the CV (0-255).
        :param callback: A function to be called with the written CV value. Arguments are (cv, value), -1 is a failure.
        """
        self.controller.send_command(F"<W {cv} {value}>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("r", 2, callback))

    def write_dcc_address(self, address: int, callback: Callable[[int], None]) -> None:
        """Writes the target DCC address to the locomotive. DCC-EX automatically selects between long and short addresses as needed.

        :param address: The DCC address to write to the target locomotive.
        :param callback: A function to be called with the read CV value. Arguments are (address), -1 is a failure.
        """
        self.controller.send_command(F"<W {address}>")
        if callback is not None:
            self._awaitingCallbacks.append(ExpectedCallback("w", 1, callback))

    def _command_received(self, command: DecodedCommand) -> None:
        """Internal listener to catch changes on the command station both caused by this program and other connections.

        :param command: The command we received after parsing it into a helper class.
        """
        callbackUsed: ExpectedCallback | None = None
        for possibleCallback in self._awaitingCallbacks:
            if possibleCallback._response_received(command):
                callbackUsed = possibleCallback
                break

        if callbackUsed is not None:
            self._awaitingCallbacks.remove(callbackUsed)
