from enum import IntFlag, auto, StrEnum


class DecodedCommand:
    def __init__(self, command: bytes) -> None:
        self.raw_cmd: bytes = command
        self.str_command: str = command.decode()

        properties: list[str] = self.str_command.strip("<>").split(" ")

        self.command: str = properties[0]
        self.args: list[str] = properties[1:]


class ActiveState(StrEnum):
    ON = "1"
    OFF = "0"


class Track(StrEnum):
    MAIN = "MAIN"
    PROG = "PROG"
    BOTH = "JOIN"


class Direction(StrEnum):
    FORWARD = "1"
    REVERSED = "0"


class IFlag(IntFlag):
    INVERTED = auto()
    DONT_RESTORE = auto()
    DEFAULT_ACTIVE = auto()


class TurnoutControl(StrEnum):
    DCC = "DCC"
    SERVO = "SERVO"
    VPIN = "VPIN"
    LCN = "LCN"


class TurnoutProfiles(StrEnum):
    IMMEDIATE = "0"
    HALF_SECOND = "1"
    ONE_SECOND = "2"
    TWO_SECONDS = "3"
    SEMAPHORE_BOUNCE = "4"


class TurnoutState(StrEnum):
    CLOSED = "0"
    THROWN = "1"
