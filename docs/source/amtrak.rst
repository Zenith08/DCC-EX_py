:orphan:

Amtrak Sound Example
====================

The goal of this project was a single train running around the tracks with sound cues based on sensors. The locomotive is a DCC+Sound Enabled Walthers Mainline F40 Phase 2.
Here is a video of the final result:

.. image:: http://img.youtube.com/vi/8A_f9tJLWSE/0.jpg
    :target: https://youtu.be/8A_f9tJLWSE

First, the script establishes a connection to the server, then we create local representations of all of the objects on the railroad we will be interacting with.
.. code-block::

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

It is not strictly necessary to get the turnouts, they are only retrieved here to ensure they start in the correct (straight-on) position.

This project uses asyncio to allow multiple things to happen at once. :code:`async def main()` is the entry point for that.
.. code-block::

    async def main() -> None:
        command.track_power.power_select_track(ActiveState.ON, Track.MAIN)
        print("Track power on.")
        await asyncio.sleep(1)
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(startup_sequence())
            task2 = tg.create_task(turnout_fix())

Here we see 2 tasks started, one checks that all the turnouts are correctly set. This is especially important because DCC-EX can get out of sync with what it expects turnouts to be and what they physically are.
The other begins the startup sound sequence on the locomotive (if sound is enabled). During this time the locomotive won't move so this is a way to make the main loop wait until that is done.

Now we have the loop.
First, :code:`await horn_sequence(1)` invokes another task to play the horn for 1 second.
.. code-block::

    async def horn_sequence(timeInSecs: float) -> None:
        """Asynchronously plays the horn for the specified lenght of time"""
        print(f"Horn start {timeInSecs}")
        if soundLevel >= SoundLevel.HORN_AND_BELL:
            amtrak.set_function(2, ActiveState.ON)
            await asyncio.sleep(timeInSecs)
            amtrak.set_function(2, ActiveState.OFF)

        print("Horn ended.")

After that, the train starts moving with :code:`amtrak.set_speed(60, Direction.FORWARD)`.
From here, the main workflow with this API is meant to be a series of commands to the train separated by await calls for different sensors or triggers.
This code covers the first entire loop of the train around the track.
.. code-block::

    amtrak.set_speed(60, Direction.FORWARD)
    print("Train moving.")
    await beforeCrossing.active()
    print("At crossing")
    bell_on()
    asyncio.tasks.create_task(crossing_horn())
    await afterCrossing.active()
    print("Crossing cleared")
    bell_off()

When the train starts, we use asyncio to await the train arriving at the next crossing. Then play the horn and bell when it arrives at the crossing.
Notibly here though, while at the start of the loop we used :code:`await horn_sequence(1)`, this time we use :code:`asyncio.tasks.create_task(crossing_horn())` allowing the horn to be played while the main loop keeps running.

The full source code is below:

.. literalinclude:: ../amtrak.py
   :language: python
   :linenos:
