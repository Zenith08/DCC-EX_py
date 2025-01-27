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
            errorMessages.append(f"test_live_basics: Expected CV 8, got CV {cv}.")
        if value != 129:
            errorMessages.append(f"test_live_basics: Expected to read 129 (Digitrax ID), got {value}.")

        # Else test passes
        print("test_live_basics Passed")
        test_complete.set()

    commandStation.programming.read_cv(8, local_callback)
    if not test_complete.wait(10):
        errorMessages.append("test_live_basics: Code timed out when reading CV.")


def test_write_basic():
    """Basic test to read decoder address, reset decoder address, and re-write decoder address."""
    global errorMessages

    test_complete: Event = threading.Event()

    address = 0

    def validate_address_restored(addr: int):
        nonlocal address
        if addr != address:
            errorMessages.append(f"test_write_basic: DCC Address not restored, expected {address} got {addr}.")
            test_complete.set()
            return
        # else test has passed
        print("test_write_basics Passed.")
        test_complete.set()

    def reset_address_callback(addr: int):
        nonlocal address
        if addr != 3:
            errorMessages.append(f"test_write_basics: DCC Address not reset, expected 3, got {addr}.")
            test_complete.set()
            return
        commandStation.programming.write_dcc_address(address, validate_address_restored)

    def write_callback(cv: int, value: int):
        if cv != 0:
            errorMessages.append(f"test_write_basics: Incorrect CV write, expected 8, got {cv}.")
            test_complete.set()
            return
        elif value != 0:
            errorMessages.append(f"test_write_basics: Incorrect value written, expected 0, got {value}.")
            test_complete.set()
            return
        commandStation.programming.read_dcc_address(reset_address_callback)

    def address_callback(addr: int):
        nonlocal address
        address = addr
        commandStation.programming.write_cv(8, 0, write_callback)

    # Entrypoint
    commandStation.programming.read_dcc_address(address_callback)

    if not test_complete.wait(10):
        errorMessages.append("test_live_basics: Code timed out when reading CV.")


if __name__ == "__main__":
    # Do all tests
    test_live_basics()
    test_write_basic()

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
