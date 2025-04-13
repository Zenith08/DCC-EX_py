"""A test system called by Github Actions separately to run tests on real hardware.
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
    print("Starting read write test")
    test_complete: Event = threading.Event()

    address = 0

    def validate_address_restored(addr: int):
        print(f"Checking the original address was restored correctly, got {addr}")
        if addr != address:
            errorMessages.append(f"test_write_basic: DCC Address not restored, expected {address} got {addr}.")
            test_complete.set()
            return
        # else test has passed
        print("test_write_basics Passed.")
        test_complete.set()

    def did_reset_address_callback(addr: int):
        print(f"Checking address after reset, got {addr}")
        if addr != 3:
            errorMessages.append(f"test_write_basics: DCC Address not reset, expected 3, got {addr}.")
            test_complete.set()
            return
        commandStation.programming.write_dcc_address(address, validate_address_restored)

    def write_callback(cv: int, value: int):
        print(f"Wrote {value} to cv {cv}")
        if cv != 8:
            errorMessages.append(f"test_write_basics: Incorrect CV write, expected 8, got {cv}.")
            test_complete.set()
            return
        elif value != 8:
            errorMessages.append(f"test_write_basics: Incorrect value written, expected 0, got {value}.")
            test_complete.set()
            return
        commandStation.programming.read_dcc_address(did_reset_address_callback)

    def address_callback(addr: int):
        print(f"Got the initial address read {addr}")
        nonlocal address
        address = addr
        commandStation.programming.write_cv(8, 8, write_callback)

    # Entrypoint
    commandStation.programming.read_dcc_address(address_callback)

    if not test_complete.wait(30):
        errorMessages.append("test_write_basics: Code timed out during execution.")


if __name__ == "__main__":
    print("Starting live tests...")
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
