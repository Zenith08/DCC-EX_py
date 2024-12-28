import pytest

from .TestHelpers import MockDCCEX
from dcc_ex_py.CVProgrammer import CVProgrammer
from dcc_ex_py.Helpers import ActiveState


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_set_cv_bit_main(mock_ex: MockDCCEX):
    programmer: CVProgrammer = CVProgrammer(mock_ex)

    programmer.write_cv_bit_main(1, 29, 2, ActiveState.ON)
    assert mock_ex.last_command_received == "<b 1 29 2 1>"

