# import pytest

# from .TestHelpers import MockDCCEX
from dcc_ex_py.Helpers import DecodedCommand


def test_decoded_command_no_args():
    command: DecodedCommand = DecodedCommand("<1>\n".encode())

    assert command.command == '1'
    assert len(command.args) == 0
    assert command.raw_cmd == "<1>\n".encode()
    assert command.str_command == "<1>\n"


def test_decoded_command_large():
    # Switch creation for switch id 6, SERVO mode, pin 36, thrown position 255, closed position 312, profile 0, closed (0).
    command: DecodedCommand = DecodedCommand("<H 6 SERVO 36 255 312 0 0>\n".encode())

    assert command.command == 'H'
    assert len(command.args) == 7
    assert command.args == ["6", "SERVO", "36", "255", "312", "0", "0"]
