import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.Memory import Memory


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX('192.168.4.1', 2560)


def test_memory_save_command(mock_ex):
    memory: Memory = Memory(mock_ex)

    memory.save_eeprom()
    assert mock_ex.last_command_received == "<E>"


def test_memory_delete_command(mock_ex):
    memory: Memory = Memory(mock_ex)

    memory.delete_eeprom()
    assert mock_ex.last_command_received == "<e>"
