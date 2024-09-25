import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.DigitalOutputs import DigitalOutputs, DigitalOutput
from dcc_ex_py.Helpers import ActiveState, IFlag

@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX('192.168.4.1', 2560)

def test_create_output_pin(mock_ex):
    outputs: DigitalOutputs = DigitalOutputs(mock_ex)

    outputs.create_output_pin(1, 36, IFlag(0))
    assert mock_ex.last_command_received == "<Z 1 36 0>"
