import pytest

from .TestHelpers import MockDCCEX, MockCallback
from dcc_ex_py.CVProgrammer import CVProgrammer, ExpectedCallback
from dcc_ex_py.Helpers import ActiveState, DecodedCommand


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_callback_receiver_valid():
    callbackMock: MockCallback = MockCallback()
    callbackStore: ExpectedCallback = ExpectedCallback("a", 1, callbackMock)

    assert callbackStore.cmdKey == "a"
    assert callbackStore.expectedArgs == 1
    assert callbackStore.callback == callbackMock
    callbackMock.assert_not_called()

    assert callbackStore._response_received(DecodedCommand("<a 10>\n".encode())) is True
    callbackMock.assert_called_once_with(10)

    callbackMock2: MockCallback = MockCallback()
    callbackStore2: ExpectedCallback = ExpectedCallback("r", 4, callbackMock2)

    assert callbackStore2.cmdKey == "r"
    assert callbackStore2.expectedArgs == 4
    assert callbackStore2.callback == callbackMock2
    callbackMock2.assert_not_called()

    assert callbackStore2._response_received(DecodedCommand("<r -1 2 3 -4>\n".encode())) is True
    callbackMock2.assert_called_once_with(-1, 2, 3, -4)


def test_callback_receiver_invalid():
    callbackMock: MockCallback = MockCallback()
    callbackStore: ExpectedCallback = ExpectedCallback("a", 1, callbackMock)

    assert callbackStore.cmdKey == "a"
    assert callbackStore.expectedArgs == 1
    assert callbackStore.callback == callbackMock
    callbackMock.assert_not_called()

    # Wrong key, wrong number of args
    assert callbackStore._response_received(DecodedCommand("<b 3 4>\n".encode())) is False
    callbackMock.assert_not_called()

    # Wrong key, right number of args
    assert callbackStore._response_received(DecodedCommand("<b 1>\n".encode())) is False
    callbackMock.assert_not_called()

    # Right key, wrong number of args
    assert callbackStore._response_received(DecodedCommand("<a 2 3>\n".encode())) is False
    callbackMock.assert_not_called()

    # Right key, right number of args
    assert callbackStore._response_received(DecodedCommand("<a 3>\n".encode())) is True
    callbackMock.assert_called_once_with(3)


def test_write_cv_bit_main(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)

    programmer.write_cv_bit_main(1, 29, 2, ActiveState.ON)
    assert mock_ex.last_command_received == "<b 1 29 2 1>"

    programmer.write_cv_bit_main(4, 8, 6, ActiveState.OFF)
    assert mock_ex.last_command_received == "<b 4 8 6 0>"


def test_write_cv_main(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)

    programmer.write_cv_main(6, 8, 0)
    assert mock_ex.last_command_received == "<w 6 8 0>"

    programmer.write_cv_main(12, 3, 2)
    assert mock_ex.last_command_received == "<w 12 3 2>"


def test_read_cv(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)
    callbackMock: MockCallback = MockCallback()

    programmer.read_cv(3, callbackMock)
    assert mock_ex.last_command_received == "<R 3>"
    callbackMock.assert_not_called()

    programmer._command_received(DecodedCommand("<v 3 8>\n".encode()))
    callbackMock.assert_called_once_with(3, 8)


def test_read_dcc_address(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)
    callbackMock: MockCallback = MockCallback()

    programmer.read_dcc_address(callbackMock)
    assert mock_ex.last_command_received == "<R>"
    callbackMock.assert_not_called()

    programmer._command_received(DecodedCommand("<r 3>\n".encode()))
    callbackMock.assert_called_once_with(3)


def test_verify_cv_bit(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)

    programmer.verify_cv_bit(3, 1, ActiveState.ON, MockCallback())
    assert mock_ex.last_command_received == "<V 3 1 1>"


def test_verify_cv(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)
    callbackMock: MockCallback = MockCallback()

    programmer.verify_cv(9, 10, callbackMock)
    assert mock_ex.last_command_received == "<V 9 10>"
    callbackMock.assert_not_called()

    programmer._command_received(DecodedCommand("<v 9 9>\n".encode()))
    callbackMock.assert_called_once_with(9, 9)


def test_write_cv_bit(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)

    programmer.write_cv_bit(25, 3, ActiveState.ON)
    assert mock_ex.last_command_received == "<B 25 3 1>"

    programmer.write_cv_bit(26, 1, ActiveState.OFF)
    assert mock_ex.last_command_received == "<B 26 1 0>"


def test_write_cv(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)
    callbackMock: MockCallback = MockCallback()

    programmer.write_cv(260, 242, callbackMock)
    assert mock_ex.last_command_received == "<W 260 242>"
    callbackMock.assert_not_called()

    programmer._command_received(DecodedCommand("<r 260 242>".encode()))
    callbackMock.assert_called_once_with(260, 242)


def test_write_dcc_address(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)
    callbackMock: MockCallback = MockCallback()

    programmer.write_dcc_address(92, callbackMock)
    assert mock_ex.last_command_received == "<W 92>"

    programmer._command_received(DecodedCommand("<w 92>\n".encode()))
    callbackMock.assert_called_once_with(92)
