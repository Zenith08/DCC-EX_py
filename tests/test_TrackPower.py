import pytest

from dcc_ex_py.Helpers import ActiveState

from .TestHelpers import MockDCCEX
from dcc_ex_py.TrackPower import TrackPower


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_power_on(mock_ex):
    power: TrackPower = TrackPower(mock_ex)

    power.power_all_tracks(ActiveState.ON)
    assert mock_ex.last_command_received == "<1>"

    power.power_all_tracks(ActiveState.OFF)
    assert mock_ex.last_command_received == "<0>"
