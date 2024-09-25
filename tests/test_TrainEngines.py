import pytest

from dcc_ex_py.Helpers import ActiveState, Direction

from .TestHelpers import MockDCCEX
from dcc_ex_py.TrainEngines import TrainEngines

@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX('192.168.4.1', 2560)

def test_set_speed(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engines.set_speed(4, 64, Direction.FORWARD)
    assert mock_ex.last_command_received == "<t 1 4 64 1>"

    engines.set_speed(4, 28, Direction.REVERSED)
    assert mock_ex.last_command_received == "<t 1 4 28 0>"

    engines.set_speed(1, 126, Direction.FORWARD)
    assert mock_ex.last_command_received == "<t 1 1 126 1>"

    engines.set_speed(8, 76, Direction.REVERSED)
    assert mock_ex.last_command_received == "<t 1 8 76 0>"
