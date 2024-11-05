import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.AccessoryDecoders import Accessories
from dcc_ex_py.Helpers import ActiveState


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_set_decoder(mock_ex: MockDCCEX):
    accessories: Accessories = Accessories(mock_ex)

    accessories.set_accessory_decoder(2, ActiveState.ON)
    assert mock_ex.last_command_received == "<a 2 1>"

    accessories.set_accessory_decoder(5, ActiveState.ON)
    assert mock_ex.last_command_received == "<a 5 1>"

    accessories.set_accessory_decoder(2, ActiveState.OFF)
    assert mock_ex.last_command_received == "<a 2 0>"


def test_set_decoder_subaddress(mock_ex: MockDCCEX):
    accessories: Accessories = Accessories(mock_ex)

    accessories.set_accessory_decoder_subaddress(3, 0, ActiveState.ON)
    assert mock_ex.last_command_received == "<a 3 0 1>"

    accessories.set_accessory_decoder_subaddress(3, 1, ActiveState.ON)
    assert mock_ex.last_command_received == "<a 3 1 1>"

    accessories.set_accessory_decoder_subaddress(4, 0, ActiveState.OFF)
    assert mock_ex.last_command_received == "<a 4 0 0>"

    accessories.set_accessory_decoder_subaddress(3, 0, ActiveState.OFF)
    assert mock_ex.last_command_received == "<a 3 0 0>"
