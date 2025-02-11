import asyncio
from dcc_ex_py.DCCEX import DCCEX
from dcc_ex_py.Sensors import Sensor
from dcc_ex_py.Turnouts import Turnout
from dcc_ex_py.TrainEngines import TrainEngine
from dcc_ex_py.DigitalOutputs import DigitalOutput
from dcc_ex_py.Helpers import ActiveState, Direction, IFlag, Track, TurnoutState

from dcc_ex_py.asyncsensor.AsyncSensor import AsyncSensor

## Init everything
command: DCCEX = DCCEX("192.168.4.1", 2560)

# Sensors
befCrossingRoot: Sensor = command.sensors.define_sensor(1, 49, False)
beforeCrossing: AsyncSensor = AsyncSensor(befCrossingRoot)

stationStopCWRoot: Sensor = command.sensors.define_sensor(3, 47, False)
stationStopCW: AsyncSensor = AsyncSensor(stationStopCWRoot)
stationStopCCWRoot: Sensor = command.sensors.define_sensor(4, 30, False)
stationStopCCW: AsyncSensor = AsyncSensor(stationStopCCWRoot)

mainline1StartRoot: Sensor = command.sensors.define_sensor(2, 45, False)
mainline1Start: AsyncSensor = AsyncSensor(mainline1StartRoot)
mainline1EndRoot: Sensor = command.sensors.define_sensor(5, 24, False)
mainline1End: AsyncSensor = AsyncSensor(mainline1EndRoot)
mainline2EndRoot: Sensor = command.sensors.define_sensor(6, 26, False)
mainline2End: AsyncSensor = AsyncSensor(mainline2EndRoot)
mainline2StartRoot: Sensor = command.sensors.define_sensor(7, 43, False)
mainline2Start: AsyncSensor = AsyncSensor(mainline2StartRoot)

tramStationStopRoot: Sensor = command.sensors.define_sensor(8, 28, False)
tramStationStop: AsyncSensor = AsyncSensor(tramStationStopRoot)

# Turnouts
stationCCW: Turnout = command.turnouts.create_dcc_turnout(1001, 1)
stationCW: Turnout = command.turnouts.create_dcc_turnout(1004, 4)

mainlineFront: Turnout = command.turnouts.create_dcc_turnout(1002, 2)
mainlineBack: Turnout = command.turnouts.create_dcc_turnout(1005, 5)

tramStation: Turnout = command.turnouts.create_dcc_turnout(1003, 3)

# Output
crossing: DigitalOutput = command.digitalOutputs.create_output_pin(52, 52, IFlag.SET_STATE_ON_POWER_UP | IFlag.INACTIVE_ON_POWER_UP | IFlag.FORWARD_OPERATION)

# Trains
westernMaryland: TrainEngine = command.train_engines.get_engine(1)
snowBlower: TrainEngine = command.train_engines.get_engine(7)

canadianPacific: TrainEngine = command.train_engines.get_engine(2)

tram: TrainEngine = command.train_engines.get_engine(3)


async def init_turnouts():
    """Toggles all of the turnouts into the right state"""
    print("Applying turnout check.")
    await asyncio.sleep(0.5)
    stationCCW.set_state(TurnoutState.THROWN)
    stationCW.set_state(TurnoutState.THROWN)
    mainlineFront.set_state(TurnoutState.THROWN)
    mainlineBack.set_state(TurnoutState.THROWN)
    tramStation.set_state(TurnoutState.CLOSED) # this one is inverted
    await asyncio.sleep(1)
    stationCCW.set_state(TurnoutState.CLOSED)
    stationCW.set_state(TurnoutState.CLOSED)
    mainlineFront.set_state(TurnoutState.CLOSED)
    mainlineBack.set_state(TurnoutState.CLOSED)
    tramStation.set_state(TurnoutState.THROWN)
    await asyncio.sleep(1)
    print("Turnout check complete.")


async def snow_blower_route():
    """Route planning for the WM loco and snowblower."""
    westernMaryland.set_function(0, ActiveState.ON)
    snowBlower.set_function(0, ActiveState.ON)

    while True:
        print("WM: Waiting for CP to reach main 2 end")
        await mainline2End.active()
        stationCW.set_state(TurnoutState.THROWN)

        print("WM: CP has arrived, moving")
        westernMaryland.set_speed(80, Direction.FORWARD)
        await asyncio.sleep(5)
        snowBlower.set_speed(126, Direction.FORWARD)

        await mainline1End.active()
        print("WM: At the back, switching the turnout to our favor. Continuing to mainline 1 start.")
        mainlineBack.set_state(TurnoutState.CLOSED)

        await beforeCrossing.active()
        snowBlower.set_speed(0, Direction.FORWARD)
        stationCW.set_state(TurnoutState.CLOSED)

        await mainline1Start.active()
        print("WM: At Mainline 1 start, timing a stop.")
        await asyncio.sleep(3)

        westernMaryland.set_speed(0, Direction.FORWARD)

        await stationStopCCW.active()
        await asyncio.sleep(5)
        print("WM: Backing up to service mainline 2")
        mainlineFront.set_state(TurnoutState.CLOSED)

        westernMaryland.set_speed(60, Direction.REVERSED)
        await beforeCrossing.active()
        print("WM: At reverse point, switching directions.")
        westernMaryland.set_speed(0, Direction.FORWARD)
        await asyncio.sleep(1)
        mainlineFront.set_state(TurnoutState.THROWN)
        await asyncio.sleep(1)

        print("WM: Progressing around track 2 back to siding")
        westernMaryland.set_speed(90, Direction.FORWARD)
        await mainline2Start.active()
        snowBlower.set_speed(126, Direction.FORWARD)
        westernMaryland.set_speed(80, Direction.FORWARD)

        await mainline2End.active()
        mainlineBack.set_state(TurnoutState.THROWN)
        stationCCW.set_state(TurnoutState.THROWN)
        mainlineFront.set_state(TurnoutState.CLOSED)

        await beforeCrossing.active()
        snowBlower.set_speed(0, Direction.FORWARD)

        westernMaryland.set_speed(50, Direction.FORWARD)
        await stationStopCCW.active()
        print("WM: Arrived at siding, stopping.")
        westernMaryland.set_speed(0, Direction.FORWARD)

        print("WM: Stopped, end of loop.")
        # reset
        stationCCW.set_state(TurnoutState.CLOSED)

        # Common wait, everything should be here by now
        await asyncio.sleep(5)
        print("WM: Starting new loop")


async def freight_train_route():
    """Route planning for the CP freight train."""
    canadianPacific.set_function(0, ActiveState.ON)
    
    while True:
        print("CP: Starting motion until Mainline 2 Start.")
        mainlineBack.set_state(TurnoutState.THROWN)
        canadianPacific.set_speed(95, Direction.FORWARD)

        await mainline2Start.active()
        print("CP: Arrived at mainline 2 start. Waiting for tram to reach main 1 back")
        canadianPacific.set_speed(0, Direction.FORWARD)

        await asyncio.sleep(15)

        print("CP: Timed wait for WM complet, awaiting tram.")
        await mainline1End.active()
        print("CP: Tram at back, progressing slowly. Waiting for station stop.")
        stationCCW.set_state(TurnoutState.CLOSED)
        mainlineFront.set_state(TurnoutState.THROWN)
        canadianPacific.set_speed(60, Direction.FORWARD)

        await stationStopCCW.active()
        print("CP: Tram at station stop CCW, speeding up")
        stationCW.set_state(TurnoutState.CLOSED)
        canadianPacific.set_speed(75, Direction.FORWARD)

        await mainline1End.active()
        print("At back of track, progressing to start.")
        await mainline1Start.active()
        print("CP: At start point, stopping.")
        canadianPacific.set_speed(0, Direction.FORWARD)

        print("CP: Loop Complete")

        await stationStopCCW.active()
        print("CP: Detected WM completing loop, queuing next loop.")
        
        # Everything should be here now
        await asyncio.sleep(5)
        print("CP: Starting new loop")
        # await asyncio.sleep(10000)


async def tram_route():
    """Route planning for the tram."""
    tram.set_function(0, ActiveState.ON)

    while True:
        print("T: Awaiting WM to move to mainline 1 end")
        await mainline1End.active()
        tramStation.set_state(TurnoutState.CLOSED)
        tram.set_speed(100, Direction.FORWARD)
        print("T: Moving to Station Stop CCW")
        await stationStopCW.active()
        tram.set_speed(0, Direction.FORWARD)

        print("T: At station stop. Awaiting WM stopping")
        await mainline1Start.active()
        await asyncio.sleep(4)

        stationCCW.set_state(TurnoutState.THROWN)
        mainlineBack.set_state(TurnoutState.CLOSED)
        tram.set_speed(126, Direction.FORWARD)
        print("T: Leaving station, progressing to main 1 back")

        await mainline1End.active()
        print("T: At back of track, prepping entering station")
        tramStation.set_state(TurnoutState.THROWN)
        stationCW.set_state(TurnoutState.THROWN)

        await stationStopCW.active()
        tram.set_speed(0, Direction.FORWARD)
        print("T: At turnaround, reversing")
        await asyncio.sleep(2)
        tram.set_speed(0, Direction.REVERSED)
        await asyncio.sleep(1)
        tramStation.set_state(TurnoutState.CLOSED)
        await asyncio.sleep(1)

        tram.set_speed(70, Direction.REVERSED)
        print("T: Reversing into tram station")
        await tramStationStop.active()
        tram.set_speed(0, Direction.REVERSED)
        print("T: Stopped at station, awaiting loop.")
        await asyncio.sleep(4)
        tram.set_speed(0, Direction.FORWARD)
        tramStation.set_state(TurnoutState.THROWN)
        print("T: Loop complete.")

        await stationStopCCW.active()
        print("T: Detected WM completing loop. Queuing next loop.")
        # Everything should be here by now.
        await asyncio.sleep(5)
        print("T: Starting new loop")


async def main():
    command.track_power.power_select_track(ActiveState.ON, Track.MAIN)
    await asyncio.sleep(1)
    await init_turnouts()

    print("Startup complete.")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(snow_blower_route())
        task2 = tg.create_task(freight_train_route())
        task3 = tg.create_task(tram_route())


# normal python start, init async code.
if __name__ == "__main__":
    asyncio.run(main())
