import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.Sensors import Sensors


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_delete_sensor(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    sensors.delete_sensor(2)
    assert mock_ex.last_command_received == "<S 2>"
