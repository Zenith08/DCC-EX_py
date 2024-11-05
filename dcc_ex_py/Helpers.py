"""Holds a collection of Enums and Types used to make function arguments human readable and enable strong type hint support."""
from enum import IntFlag, StrEnum


class DecodedCommand:
    """Represents a command that has been received from the server parsed into its components."""

    def __init__(self, command: bytes) -> None:
        """Parses the raw bytes received from the server into a command with arguments separated from the op code.

        :param command: The raw bytes of the command received.
        """

        self.raw_cmd: bytes = command
        """The raw bytes of the command received."""
        self.str_command: str = command.decode()
        """The decoded string of the command received."""

        properties: list[str] = self.str_command.strip("<>\n").split(" ")

        self.command: str = properties[0]
        """The first character/op code of the command received."""
        self.args: list[str] = properties[1:]
        """The remaining arguments (without op code) sent by the command station."""


class ActiveState(StrEnum):
    """A helper enum to map between the natural langauge of the digital outputs (on/off) and the numeric strings expected by the command station ("1"/"0")
    """

    ON = "1"
    OFF = "0"


class Track(StrEnum):
    """A helper enum to map which track (Main, Programming, or Both) to target.
    """
    MAIN = "MAIN"
    PROG = "PROG"
    BOTH = "JOIN"


class Direction(StrEnum):
    """A helper enum to map between the natural language of direction (Forward, Reversed) and the numeric strings expected by the command station ("1"/"0")
    """

    FORWARD = "1"
    REVERSED = "0"


class IFlag(IntFlag):
    """A helper enum to compose bit-flags for digital output configuration.
    See DCC-EX documentation for more.
    """

    FORWARD_OPERATION = 0b000  # Bit 0: forward operation
    """The pin operates normally, ON = High, OFF = Low."""
    INVERTED_OPERATION = 0b001  # Bit 0: inverted operation
    """The pin is inverted, ON = Low, OFF = High."""

    RESTORE_STATE_ON_POWER_UP = 0b000  # Bit 1: restore state on power-up
    """The state of the pin is saved to EEPROM and is restored on power-up."""
    SET_STATE_ON_POWER_UP = 0b010      # Bit 1: set state on power-up based on bit 2
    """The pin is set to a default state on power-up."""

    INACTIVE_ON_POWER_UP = 0b000  # Bit 2: set pin to INACTIVE upon power-up
    """The pin is set to OFF on power-up."""
    ACTIVE_ON_POWER_UP = 0b100    # Bit 2: set pin to ACTIVE upon power-up
    """The pin is set to ON on power-up."""


class TurnoutControl(StrEnum):
    """A helper enum to define what method a given turnout is using for control.
    DCC: An accessory decoder.
    SERVO: a servo driven by PWM.
    PIN: A digital output pin set to HIGH or LOW.
    LCN: A Layout Control Node.
    """

    DCC = "DCC"
    SERVO = "SERVO"
    PIN = "VPIN"
    LCN = "LCN"


class TurnoutProfiles(StrEnum):
    """Speed settings to use for servos controlled by the command station.
    Each represents the length of time to lerp between 1 postion and another.
    IMMEDIATE: No lerp, the new PWM value is sent.
    HALF_SECOND: Lerp over 0.5 seconds.
    ONE_SECOND: Lerp over 1.0 seconds.
    TWO_SECOND: Lerp over 2.0 seconds.
    SEMAPHORE_BOUNCE: Includes a bouncing motion as might be seen on semaphor flags.
    """

    IMMEDIATE = "0"
    HALF_SECOND = "1"
    ONE_SECOND = "2"
    TWO_SECONDS = "3"
    SEMAPHORE_BOUNCE = "4"


class TurnoutState(StrEnum):
    """A helper enum to map between the natural language of turnouts (Closed/Thrown) and the numeric strings expected by the command station ("0"/"1")
    """

    CLOSED = "0"
    THROWN = "1"
