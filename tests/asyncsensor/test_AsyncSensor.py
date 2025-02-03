from typing import Any
import pytest
import asyncio

from ..TestHelpers import DummySensor
from dcc_ex_py.asyncsensor.AsyncSensor import AsyncSensor


@pytest.mark.asyncio
async def test_active_returns_true_after_activation():
    """
    Test that the async 'active' method returns True when the sensor is activated.
    """
    # Create a dummy sensor and wrap it with AsyncSensor.
    dummy: DummySensor = DummySensor()
    async_sensor: AsyncSensor = AsyncSensor(dummy)

    # Start the asynchronous wait in the event loop.
    # This schedules async_sensor.active() which will await until a state change.
    active_future: asyncio.Task[Any] = asyncio.create_task(async_sensor.active())

    # Allow the event loop to run a little so that async_sensor.active() is pending.
    await asyncio.sleep(0.1)

    # Simulate sensor activation.
    dummy.simulate_state_change(active=True)

    # Await the result of active(). It should return True.
    result: bool = await active_future
    assert result is True


@pytest.mark.asyncio
async def test_no_activation_does_not_complete():
    """
    Test that the async 'active' method does not complete if the sensor is not activated.
    We use a timeout to ensure that the coroutine remains pending.
    """
    dummy: DummySensor = DummySensor()
    async_sensor: AsyncSensor = AsyncSensor(dummy)

    # Start the asynchronous wait.
    active_future: asyncio.Task[Any] = asyncio.create_task(async_sensor.active())

    # We do not simulate any sensor activation.
    # The coroutine should not complete; we use asyncio.wait_for with a short timeout.
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(active_future, timeout=0.2)


@pytest.mark.asyncio
async def test_inactive_state_does_not_trigger_callback():
    """
    Test that when the sensor is simulated with inactive state (False),
    the active() method does not complete.
    """
    dummy: DummySensor = DummySensor()
    async_sensor: AsyncSensor = AsyncSensor(dummy)

    active_future: asyncio.Task[Any] = asyncio.create_task(async_sensor.active())

    # Simulate sensor inactive state.
    dummy.simulate_state_change(active=False)

    # The active() coroutine should still be pending since only an active (True) state triggers completion.
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(active_future, timeout=0.2)
