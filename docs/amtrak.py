import asyncio
import signal
import sys
import time

from enum import IntEnum
from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Helpers import ActiveState, Direction, Track, TurnoutState
from dcc_ex_py.Sensors import Sensor
from dcc_ex_py.Turnouts import Turnout
from dcc_ex_py.TrainEngines import TrainEngine

from dcc_ex_py.asyncsensor.AsyncSensor import AsyncSensor

## Init everything
command: DCCEX = DCCEX("192.168.4.1", 2560)

befCrossingRoot: Sensor = command.sensors.define_sensor(1, 49, False)
beforeCrossing: AsyncSensor = AsyncSensor(befCrossingRoot)

aftCrossingRoot: Sensor = command.sensors.define_sensor(2, 45, False)
afterCrossing: AsyncSensor = AsyncSensor(aftCrossingRoot)

stationCCW: Turnout = command.turnouts.create_dcc_turnout(1001, 1)
stationCW: Turnout = command.turnouts.create_dcc_turnout(1004, 4)
mainlineFront: Turnout = command.turnouts.create_dcc_turnout(1002, 2)
mainlineBack: Turnout = command.turnouts.create_dcc_turnout(1005, 5)

amtrak: TrainEngine = command.train_engines.get_engine(5)

class SoundLevel(IntEnum):
    NONE = 0
    HORN_AND_BELL = 1
    DYNAMIC_BREAK = 2
    FULL = 3

soundLevel: SoundLevel = SoundLevel.FULL

running: bool = True

async def startup_sequence() -> None:
    """Run the startup sequence and wait for it to finish"""
    print("Engine startup sequence running.")
    amtrak.set_function(0, ActiveState.ON) # Headlight

    if soundLevel == SoundLevel.FULL:
        amtrak.set_function(8, ActiveState.ON)
        await asyncio.sleep(20)
    
    print("Engine startup sequence complete.")

async def turnout_fix() -> None:
    """Toggles all of the turnouts into the right state"""
    print("Applying turnout check.")
    await asyncio.sleep(0.5)
    stationCCW.set_state(TurnoutState.THROWN)
    stationCW.set_state(TurnoutState.THROWN)
    mainlineFront.set_state(TurnoutState.THROWN)
    mainlineBack.set_state(TurnoutState.THROWN)
    await asyncio.sleep(1)
    stationCCW.set_state(TurnoutState.CLOSED)
    stationCW.set_state(TurnoutState.CLOSED)
    mainlineFront.set_state(TurnoutState.CLOSED)
    mainlineBack.set_state(TurnoutState.CLOSED)
    await asyncio.sleep(1)
    print("Turnout check complete.")

async def horn_sequence(timeInSecs: float) -> None:
    """Asynchronously plays the horn for the specified lenght of time"""
    print(f"Horn start {timeInSecs}")
    if soundLevel >= SoundLevel.HORN_AND_BELL:
        amtrak.set_function(2, ActiveState.ON)
        await asyncio.sleep(timeInSecs)
        amtrak.set_function(2, ActiveState.OFF)
    print("Horn ended.")

def bell_on() -> None:
    """Helper to play the bell sound"""
    if soundLevel >= SoundLevel.HORN_AND_BELL:
        amtrak.set_function(1, ActiveState.ON)

def bell_off() -> None:
    """Helper to turn the bell off"""
    amtrak.set_function(1, ActiveState.OFF)

def dyn_break_on() -> None:
    """Helper to turn the dynamic break on"""
    if soundLevel >= SoundLevel.DYNAMIC_BREAK:
        amtrak.set_function(4, ActiveState.ON)

def dyn_break_off() -> None:
    """Helper to turn the dynamic break off"""
    amtrak.set_function(4, ActiveState.OFF)

async def crossing_horn():
    await asyncio.sleep(0.05)
    await horn_sequence(0.35)
    await asyncio.sleep(0.2)
    await horn_sequence(0.75)


async def main() -> None:
    command.track_power.power_select_track(ActiveState.ON, Track.MAIN)
    print("Track power on.")
    await asyncio.sleep(1)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(startup_sequence())
        task2 = tg.create_task(turnout_fix())


    while(running):
        await horn_sequence(1)

        amtrak.set_speed(60, Direction.FORWARD)
        print("Train moving.")

        await beforeCrossing.active()
        print("At crossing")
        bell_on()
        asyncio.tasks.create_task(crossing_horn())

        await afterCrossing.active()
        print("Crossing cleared")
        bell_off()

        # Hopefully we don't need this but just in case wait for a second.
        await asyncio.sleep(10)

        # On the second loop time a stop

        await beforeCrossing.active()
        print("At crossing")
        bell_on()
        asyncio.tasks.create_task(crossing_horn())

        # Start slowdown
        dyn_break_on()
        amtrak.set_speed(45, Direction.FORWARD)

        await afterCrossing.active()
        print("Crossing cleared")
        # bell_off()
        dyn_break_off()

        await asyncio.sleep(4.5)
        amtrak.set_speed(0, Direction.FORWARD)

        print("Train stopped.")

        await asyncio.sleep(1)
        bell_off()

        # Wait a bit before starting again
        await asyncio.sleep(20)
    
    # Shutdown case
    amtrak.set_function(8, ActiveState.OFF)
    amtrak.set_function(0, ActiveState.OFF)

    await asyncio.sleep(10)
    # End task
    cleanup()


def cleanup():
    amtrak.set_speed(0, Direction.FORWARD)
    amtrak.set_function(0, ActiveState.OFF)
    amtrak.set_function(8, ActiveState.OFF)
    bell_off()
    dyn_break_off()
    command.track_power.power_select_track(ActiveState.OFF, Track.MAIN)
    time.sleep(1)
    command.quit()


def shutdown_handler(signum, frame):
    """This is on a separate thread"""
    global running

    if running:
        running = False
        print("Shutdown detected, waiting for train to stop.")
    else:
        print("2nd Keyboard Interrupt, hard quitting.")
        cleanup()
        sys.exit(0)


if __name__ == "__main__":
    # Run main
    signal.signal(signal.SIGINT, shutdown_handler)
    asyncio.run(main())
