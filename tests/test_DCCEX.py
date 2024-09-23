import pytest
from unittest.mock import MagicMock, patch

from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Helpers import DecodedCommand


@pytest.fixture
def mock_socket():
    with patch('socket.socket') as mock_sock:
        mock_sock_inst = mock_sock.return_value
        mock_sock_inst.recv = MagicMock(return_value=b'some response')
        yield mock_sock_inst


@pytest.fixture
def dccex(mock_socket):
    # Create an instance of the DCCEX class
    return DCCEX(ip="127.0.0.1", port=1234)


def test_init_sockets(mock_socket):
    dccex = DCCEX(ip="127.0.0.1", port=1234)

    # Ensure the socket is connected with the correct parameters
    mock_socket.connect.assert_called_with(("127.0.0.1", 1234))


def test_send_command(mock_socket, dccex):
    command = "power on"

    # Send a command using the send_command method
    dccex.send_command(command)

    # Verify that the command was sent with the correct encoding and added newline
    mock_socket.sendall.assert_called_with(b'power on\n')


def test_add_command_listener(dccex):
    mock_listener = MagicMock()

    # Add a listener
    dccex.add_command_listener(mock_listener)

    # Simulate receiving a message
    mock_decoded_command = MagicMock(spec=DecodedCommand)
    dccex.onPacketReceived[-1](mock_decoded_command)

    # Check that the listener was called with the decoded command
    mock_listener.assert_called_with(mock_decoded_command)


def test_remove_command_listener(dccex):
    mock_listener = MagicMock()

    # Add and then remove a listener
    dccex.add_command_listener(mock_listener)
    dccex.remove_command_listener(mock_listener)

    # Simulate receiving a message
    mock_decoded_command: DecodedCommand = DecodedCommand("<p1 1>".encode())

    if dccex.onPacketReceived:
        dccex.onPacketReceived[-1](mock_decoded_command)

    # Check that the listener is no longer called
    assert mock_listener.call_count == 0
