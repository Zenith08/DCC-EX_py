import pytest

from dcc_ex_py.Helpers import DecodedCommand

from .TestHelpers import MockDCCEX
from dcc_ex_py.Sensors import Sensors, Sensor


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_create_sensor(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    sensor: Sensor = sensors.define_sensor(1, 36, False)
    assert mock_ex.last_command_received == "<S 1 36 0>"
    assert sensor is not None
    assert sensor.id == 1
    assert sensor.pin == 36
    assert not sensor.inverted
    assert not sensor.active

    assert sensor == sensors.get_sensor(1)


def test_get_nonexistent_sensor(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    nonSensor: Sensor = sensors.get_sensor(1)
    assert nonSensor.id == -1
    assert nonSensor.pin == -1


def test_delete_sensor(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    sensors.define_sensor(2, 25, False)
    assert sensors.get_sensor(2).id == 2

    sensors.delete_sensor(2)
    assert mock_ex.last_command_received == "<S 2>"

    assert sensors.get_sensor(2).id == -1


def test_get_sensor_info(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    defineFullSensor: DecodedCommand = DecodedCommand("<Q 3 35 0>\n".encode())
    sensors._command_received(defineFullSensor)

    sensor3: Sensor = sensors.get_sensor(3)
    assert sensor3.id == 3
    assert sensor3.pin == 35

    assert not sensor3.active

    updateState: DecodedCommand = DecodedCommand("<Q 3>\n".encode())
    sensors._command_received(updateState)

    assert sensor3.active

    newSensorState: DecodedCommand = DecodedCommand("<q 4>\n".encode())
    sensors._command_received(newSensorState)

    sensor4: Sensor = sensors.get_sensor(4)
    assert sensor4.id == 4
    assert sensor4.pin == 0

    fillin: DecodedCommand = DecodedCommand("<Q 4 33 0>\n".encode())
    sensors._command_received(fillin)

    assert sensor4.pin == 33


def test_callbacks(mock_ex):
    sensors: Sensors = Sensors(mock_ex)

    global globalCallbackRan
    global localCallbackRan

    globalCallbackRan = False

    def global_sensor_callback(sensor: Sensor, id: int, state: bool) -> None:
        assert id == 2
        assert state is True
        assert sensor.id == 2
        global globalCallbackRan
        globalCallbackRan = True

    sensors.sensor_changed.append(global_sensor_callback)

    sensor2Active: DecodedCommand = DecodedCommand("<Q 2>\n".encode())
    sensors._command_received(sensor2Active)

    assert 2 in sensors.sensors
    assert globalCallbackRan is True

    localCallbackRan = False

    def local_sensor_callback(sensor: Sensor, active: bool) -> None:
        assert sensor.id == 2
        assert active is True
        global localCallbackRan
        localCallbackRan = True

    sensors.sensors[2].state_change.append(local_sensor_callback)

    sensors._command_received(sensor2Active)

    assert localCallbackRan is True
