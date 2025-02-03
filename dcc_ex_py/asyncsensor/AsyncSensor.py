import asyncio
from typing import Any
from ..Sensors import Sensor
import queue


class AsyncSensor():
    """Wraps a sensor into a reusable container that allows the use of asyncio to await for sensor conditions to be met.
    """

    def __init__(self, parent: Sensor) -> None:
        """Wraps the target sensor (which must be created by the API) in an async sensor.

        :param parent: The representation of the physical sensor to interact asynchronously with.
        """

        self._parent: Sensor = parent
        """The internal store for our own sensor. It is the only way to retrieve information about the underlying sensor of this object.
        """

        self._parent.state_change.append(self._listener)

        self._asyncQueue: asyncio.Queue[Any] = asyncio.Queue()
        """An asyncio object that handles the more involved implementations of asynchronous functions."""

        self._loops: queue.Queue[asyncio.AbstractEventLoop] = queue.Queue()
        """A local list of functions awaiting callbacks. Allows transfering callbacks from the DCC-EX listener thread onto the event loops thread."""

    def _listener(self, sensor: Sensor, active: bool) -> None:
        """Internal listener provided by the sensor when it has been activated (state changed),
        forwards that feedback onto any waiting event loops if the sensor was activated (detecting a train).

        :param sensor: The parent sensor that invoked the callback (unused).
        :param active: Whether the sensor is detecting a train (True) or not (False).
        """
        if active:
            while not self._loops.empty():
                loop: asyncio.AbstractEventLoop = self._loops.get()
                loop.call_soon_threadsafe(self._asyncQueue.put_nowait, True)

    async def active(self) -> Any:
        """The primary asynchronous function, expected to be used as `await asyncsensor.active()`,
        pauses an asyncio event loop until this sensor detects a train.

        :return: `True`, a discard value required by the Async Queue but not meaningful. (Type hint is Any to indicate this value is meaningless).
        """
        self._loops.put(asyncio.get_event_loop())
        return await self._asyncQueue.get()
