import pytest

from dcc_ex_py.Helpers import DecodedCommand, TurnoutControl, TurnoutProfiles, TurnoutState

from .TestHelpers import MockDCCEX
from dcc_ex_py.Turnouts import Turnouts, Turnout


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_create_dcc_turnout(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnout: Turnout = turnouts.create_dcc_turnout(1, 1)
    assert mock_ex.last_command_received == "<T 1 DCC 1>"

    assert turnout.id == 1

    turnout2: Turnout = turnouts.create_dcc_turnout_subaddress(2, 5, 0)
    assert mock_ex.last_command_received == "<T 2 DCC 5 0>"

    assert turnout2.id == 2


def test_create_servo_turnout(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnout: Turnout = turnouts.create_servo_turnout(1, 36, 312, 221, TurnoutProfiles.HALF_SECOND)
    assert mock_ex.last_command_received == "<T 1 SERVO 36 312 221 1>"
    assert turnout.id == 1


def test_create_vpin_turnout(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnout: Turnout = turnouts.create_gpio_turnout(3, 25)
    assert mock_ex.last_command_received == "<T 3 VPIN 25>"
    assert turnout.id == 3


def test_throw_turnouts(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnout: Turnout = turnouts.create_dcc_turnout(1, 2)

    turnouts.set_turnout(1, TurnoutState.THROWN)
    assert mock_ex.last_command_received == "<T 1 1>"

    turnout.set_state(TurnoutState.CLOSED)
    assert mock_ex.last_command_received == "<T 1 0>"


def test_delete_turnout(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnouts.create_dcc_turnout(2, 7)
    assert 2 in turnouts.turnouts

    turnouts.delete_turnout(2)
    assert mock_ex.last_command_received == "<T 2>"

    assert 2 not in turnouts.turnouts


def test_turnout_summary(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnouts.refresh_turnouts()
    assert mock_ex.last_command_received == "<T>"


def test_learn_about_turnouts(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnoutDefined: DecodedCommand = DecodedCommand("<H 1 DCC 3 0 0>".encode())
    turnouts._command_received(turnoutDefined)

    assert 1 in turnouts.turnouts
    turnout: Turnout = turnouts.turnouts[1]

    assert turnout.id == 1
    assert turnout.controlType == TurnoutControl.DCC
    assert turnout.address == 3
    assert turnout.thrown == TurnoutState.CLOSED

    turnoutChange: DecodedCommand = DecodedCommand("<H 1 1>".encode())
    turnouts._command_received(turnoutChange)

    assert turnout.thrown == TurnoutState.THROWN

    turnoutPartial: DecodedCommand = DecodedCommand("<H 5 0>".encode())
    turnouts._command_received(turnoutPartial)

    assert 5 in turnouts.turnouts
    turnout5: Turnout = turnouts.turnouts[5]

    assert turnout5.id == 5
    assert turnout5.thrown == TurnoutState.CLOSED
