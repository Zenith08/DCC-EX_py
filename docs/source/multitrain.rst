:orphan:

Multiple Train Example
======================

The goal of this project was to build off the [Amtrak](https://github.com/Zenith08/DCC-EX_py/wiki/Amtrak) project, this time with 3 trains running independently. The trains are old Bachmann DCC equipped trains with no sound this time. Additionally, I added a DCC decoder to the rotary snowplow.
Here is a video of the final result:

.. image:: http://img.youtube.com/vi/ylQdYiYuVxI/0.jpg
    :target: https://youtu.be/ylQdYiYuVxI

Like last time we start with a block connecting to the DCC-EX command staiton, and creating local representations of the objects on our tracks (the sensors and turnouts).
Also like last time, the crossing is being controlled by EX-RAIL automation on the command station itself.

Once again, :code:`async def main()` is the entry point which runs a brief initialization to set track power and turnouts to the correct state.
.. code-block::

    async def main():
        command.track_power.power_select_track(ActiveState.ON, Track.MAIN)
        await asyncio.sleep(1)
        await init_turnouts()

Then, a task is started for each train and they begin to run:
.. code-block::

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(snow_blower_route())
        task2 = tg.create_task(freight_train_route())
        task3 = tg.create_task(tram_route())

Each train's task is similar to the main loop seen in the Amtrak example. This time though trains will wait for other trains (still using AsyncSensor) and will set turnouts before moving.
Here is an excerpt from the Tram's operation with some notes added:
.. code-block::

    while True:
        print("T: Awaiting WM to move to mainline 1 end")
        await mainline1End.active() # This waits for the Snow Blower train to cross a sensor point
        tramStation.set_state(TurnoutState.CLOSED) # Now we can set the track in our favour and start moving.
        tram.set_speed(100, Direction.FORWARD)
        print("T: Moving to Station Stop CCW")
        await stationStopCW.active() # This sensor is triggered by us so we know when to stop.
        tram.set_speed(0, Direction.FORWARD)

        print("T: At station stop. Awaiting WM stopping")
        await mainline1Start.active() # Once again we wait for the Snow Blower train to pass
        await asyncio.sleep(4)

Another important thing from this example is that multiple trains can await the same sensor. For example, all 3 loops end with :code:`await stationStopCCW.active()` and all 3 loops continue once the Snow Blower has triggered that sensor.

The full source code is below:

.. literalinclude:: ../multitrain.py
    :language: python
    :linenos:
