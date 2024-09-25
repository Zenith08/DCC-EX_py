import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.Turnouts import Turnouts


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX('192.168.4.1', 2560)


def test_create_dcc_turnout(mock_ex):
    turnouts: Turnouts = Turnouts(mock_ex)

    turnouts.create_dcc_turnout(1, 1)
    assert mock_ex.last_command_received == "<T 1 DCC 1>"

    turnouts.create_dcc_turnout(2, 4)
    assert mock_ex.last_command_received == "<T 2 DCC 4>"

    turnouts.create_dcc_turnout_subaddress(2, 5, 0)
    assert mock_ex.last_command_received == "<T 2 DCC 5 0>"
