import asyncio
from ..Sensors import Sensor
import queue

class AsyncSensor():
    def __init__(self, parent: Sensor):
        self._parent: Sensor = parent
        self._parent.state_change.append(self._listener)

        self._asyncQueue: asyncio.Queue = asyncio.Queue()

        self._loops: queue.Queue[asyncio.AbstractEventLoop] = queue.Queue()

    def _listener(self, sensor: Sensor, active: bool):
        # print(f"Listener received feedback for sensor {self._parent.id}, active: {active}")
        if active:
            while not self._loops.empty():
                loop: asyncio.AbstractEventLoop = self._loops.get()
                loop.call_soon_threadsafe(self._asyncQueue.put_nowait, True)

    async def active(self):
        # print(f"Something is awaiting sensor {self._parent.id}")
        self._loops.put(asyncio.get_event_loop())
        return await self._asyncQueue.get()
