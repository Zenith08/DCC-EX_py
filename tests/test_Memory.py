import pytest

from dcc_ex_py.Helpers import DecodedCommand

from .TestHelpers import MockDCCEX
from dcc_ex_py.Memory import Memory


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_memory_save_command(mock_ex):
    memory: Memory = Memory(mock_ex)

    memory.save_eeprom()
    assert mock_ex.last_command_received == "<E>"


def test_memory_delete_command(mock_ex):
    memory: Memory = Memory(mock_ex)

    memory.delete_eeprom()
    assert mock_ex.last_command_received == "<e>"


def test_recieve_saved_information(mock_ex):
    memory: Memory = Memory(mock_ex)

    eepRomInfo: DecodedCommand = DecodedCommand("<e 3 2 1>\n".encode())
    memory._command_received(eepRomInfo)

    assert memory.nTurnoutsSaved == 3
    assert memory.nSensorsSaved == 2
    assert memory.nOutputsSaved == 1

    clearMemory: DecodedCommand = DecodedCommand("<0>\n".encode())
    memory._command_received(clearMemory)

    assert memory.nTurnoutsSaved == 0
    assert memory.nSensorsSaved == 0
    assert memory.nOutputsSaved == 0
