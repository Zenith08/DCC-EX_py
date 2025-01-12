import pytest

from ..TestHelpers import MockDCCEX
from dcc_ex_py.Sensors import Sensors, Sensor


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_sensor_basic(mock_ex):
    sensors: Sensors = Sensors(mock_ex)
