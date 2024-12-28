"""A test system called by Github Actions separately to run tests on real hardware."""
from threading import Event
from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.CVProgrammer import CVProgrammer

# Globals
commandStation: DCCEX = DCCEX("10.0.0.25", 2560)
errorMessages: list[str] = []


def test_live_basics():
    """Basic test to see if the decoder is responding."""


if __name__ == "__main__":
    pass