import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.DigitalOutputs import DigitalOutputs, DigitalOutput
from dcc_ex_py.Helpers import IFlag, ActiveState, DecodedCommand


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_create_output_pin(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    output: DigitalOutput = outputs.create_output_pin(1, 36, IFlag(0))
    assert mock_ex.last_command_received == "<Z 1 36 0>"
    assert 1 in outputs.outputs
    assert output is not None

    assert output.id == 1
    assert output.pin == 36

    output.set_state(ActiveState.ON)
    assert mock_ex.last_command_received == "<Z 1 1>"


def test_learn_about_pins(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    outputChanged: DecodedCommand = DecodedCommand("<Y 3 0>\n".encode())
    assert outputChanged.command == 'Y'
    assert outputChanged.args == ['3', '0']

    outputs._command_received(outputChanged)
    assert 3 in outputs.outputs

    output3: DigitalOutput = outputs.outputs[3]
    assert output3 is not None
    assert output3.id == 3
    assert output3.pin == 0
    assert output3.state == ActiveState.OFF

    fullDefine: DecodedCommand = DecodedCommand("<Y 3 36 0 1>\n".encode())

    outputs._command_received(fullDefine)

    assert output3.pin == 36
    assert output3.state == ActiveState.ON

    output3.set_state(ActiveState.OFF)
    assert mock_ex.last_command_received == "<Z 3 0>"


def test_delete_output_pins(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    outputs.create_output_pin(1, 25, IFlag.FORWARD_OPERATION)

    assert 1 in outputs.outputs

    outputs.delete_output_pin(1)
    assert 1 not in outputs.outputs
    assert mock_ex.last_command_received == "<Z 1>"


def test_refresh_output_pins(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    outputs.refresh_output_pins()
    assert mock_ex.last_command_received == "<Z>"


def test_set_output_pins(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    output2: DigitalOutput = outputs.create_output_pin(2, 36, IFlag.FORWARD_OPERATION)

    outputs.set_output_pin(2, ActiveState.ON)
    assert mock_ex.last_command_received == "<Z 2 1>"

    output2.set_state(ActiveState.OFF)
    assert mock_ex.last_command_received == "<Z 2 0>"
