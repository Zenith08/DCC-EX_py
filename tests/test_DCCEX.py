import pytest
from time import sleep

from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Helpers import DecodedCommand

from .TestHelpers import MockTCPServer


@pytest.fixture
def mock_server():
    server = MockTCPServer(port=9999)  # Mock server on a specific port
    server.start()
    sleep(1)  # Give server time to start
    yield server
    server.stop()


def test_dccex_connection(mock_server):
    client: DCCEX = DCCEX("127.0.0.1", 9999)
    assert client is not None

    client.send_command("<1>")
    sleep(1)
    assert mock_server.last_received == "<1>\n"

    def command_listener(command: DecodedCommand):
        assert command.command == "P1"

    client.add_command_listener(command_listener)

    mock_server.send("<P1>\n")
    sleep(1)

    client.quit()


def test_add_2_listeners(mock_server):
    client: DCCEX = DCCEX("127.0.0.1", 9999)
    assert client is not None

    def command_listener_1(command: DecodedCommand):
        assert command.command == 'H'
        assert command.args == ['1', '1']

    def command_listener_2(command: DecodedCommand):
        assert command.command == 'H'
        assert command.args == ['1', '1']

    client.add_command_listener(command_listener_1)
    client.add_command_listener(command_listener_2)

    mock_server.send("<H 1 1>\n")
    sleep(1)

    client.quit()


def test_remove_listeners(mock_server):
    client: DCCEX = DCCEX("127.0.0.1", 9999)
    assert client is not None

    def command_listener_1(command: DecodedCommand):
        pytest.fail("This listener should not have been called")

    def command_listener_2(command: DecodedCommand):
        assert command.command == 'H'
        assert command.args == ['2', '0']

    client.add_command_listener(command_listener_1)
    client.add_command_listener(command_listener_2)

    client.remove_command_listener(command_listener_1)

    mock_server.send("<H 2 0>\n")
    sleep(1)

    client.quit()


def test_add_remove_listeners(mock_server):
    client: DCCEX = DCCEX("127.0.0.1", 9999)
    assert client is not None

    expectedAnswer: bool = False

    def listener_1(command: DecodedCommand):
        if expectedAnswer:
            assert command.command == 'Q'
            assert command.args == ['1']
        else:
            pytest.fail("A callback was called when it shouldn't have been")

    def listener_2(command: DecodedCommand):
        assert command.command == 'Q'
        assert command.args == ['1']

    client.add_command_listener(listener_2)

    mock_server.send("<Q 1>\n")
    sleep(1)

    client.add_command_listener(listener_1)
    expectedAnswer = True

    mock_server.send("<Q 1>\n")
    sleep(1)

    client.remove_command_listener(listener_1)
    expectedAnswer = False
    sleep(1)

    client.quit()
