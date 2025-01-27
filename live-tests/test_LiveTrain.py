"""A test system called by Github Actions separately to run tests on real hardware.
Attempt: 1
"""
import sys
import threading
from threading import Event
from dcc_ex_py.DCCEX import DCCEX

# Globals
commandStation: DCCEX = DCCEX("10.0.0.25", 2560)
errorMessages: list[str] = []


def test_live_basics():
    """Basic test to see if the decoder is responding."""
    global errorMessages

    test_complete: Event = threading.Event()

    def local_callback(cv: int, value: int):
        if cv != 8:
            errorMessages.append(f"test_live_basics: Expected CV 8, got CV {cv}")
        if value != 129:
            errorMessages.append(f"test_live_basics: Expected to read 129 (Digitrax ID), got {value}")
        
        print(f"Reading CV 8, got cv {cv} value {value}")
        # Else pass
        test_complete.set()

    commandStation.programming.read_cv(8, local_callback)
    if not test_complete.wait(10):
        errorMessages.append("test_live_basics: Code timed out when reading CV.")


if __name__ == "__main__":
    # Do all tests
    test_live_basics()

    # Process results
    if len(errorMessages) == 0:
        print("All tests passed, success.")
        sys.exit(0)
    else:
        print("Test failures occurred:")
        for message in errorMessages:
            print(f"    {message}")
        print("End of errors.")
        sys.exit(len(errorMessages))
