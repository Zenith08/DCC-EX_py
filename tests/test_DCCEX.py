import pytest
from time import sleep

from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Helpers import DecodedCommand

from .TestHelpers import MockTCPServer


@pytest.fixture
def mock_server():
    server = MockTCPServer(port=9999)  # Mock server on a specific port
    server.start()
    sleep(0.1)  # Give server time to start
    yield server
    server.stop()

def test_dccex_connection(mock_server):
    client: DCCEX = DCCEX("127.0.0.1", 9999)
    assert client is not None

    client.send_command("<1>")
    sleep(0.1)
    assert mock_server.last_received == "<1>\n"

    def command_listener(command: DecodedCommand):
        assert command.command == "P"

    client.add_command_listener(command_listener)
    mock_server.send("<P>\n")

    sleep(0.1)

    client.quit()
