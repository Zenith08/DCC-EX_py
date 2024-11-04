import pytest

from dcc_ex_py.Helpers import ActiveState, DecodedCommand, Direction

from .TestHelpers import MockDCCEX
from dcc_ex_py.TrainEngines import TrainEngine, TrainEngines


@pytest.fixture
def mock_ex() -> MockDCCEX:
    return MockDCCEX()


def test_set_speed(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engines.set_speed(4, 64, Direction.FORWARD)
    assert mock_ex.last_command_received == "<t 1 4 64 1>"

    engines.set_speed(4, 28, Direction.REVERSED)
    assert mock_ex.last_command_received == "<t 1 4 28 0>"

    engines.set_speed(1, 126, Direction.FORWARD)
    assert mock_ex.last_command_received == "<t 1 1 126 1>"

    engines.set_speed(8, 76, Direction.REVERSED)
    assert mock_ex.last_command_received == "<t 1 8 76 0>"


def test_set_cab_function(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engines.set_cab_function(1, 0, ActiveState.ON)
    assert mock_ex.last_command_received == "<F 1 0 1>"

    engines.set_cab_function(8, 3, ActiveState.OFF)
    assert mock_ex.last_command_received == "<F 8 3 0>"


def test_loco_tracking(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engines.forget_all_locos()
    assert mock_ex.last_command_received == "<->"

    engines.forget_loco(3)
    assert mock_ex.last_command_received == "<- 3>"

    engines.forget_loco(9)
    assert mock_ex.last_command_received == "<- 9>"

    engines.check_max_engines()
    assert mock_ex.last_command_received == "<#>"


def test_emergency_stop(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engines.emergency_stop()
    assert mock_ex.last_command_received == "<!>"


def test_learn_about_capacity(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    learnCapacitySmall: DecodedCommand = DecodedCommand("<# 10>\n".encode())
    engines._command_received(learnCapacitySmall)
    assert engines.maxEngines == 10

    learnCapacityLarge: DecodedCommand = DecodedCommand("<# 50>\n".encode())
    engines._command_received(learnCapacityLarge)
    assert engines.maxEngines == 50


def test_learn_about_locomotives(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engineIntroduction: DecodedCommand = DecodedCommand("<l 1 1 128 0>\n".encode())
    engines._command_received(engineIntroduction)

    assert 1 in engines.engines
    engine: TrainEngine = engines.engines[1]
    assert engine.cab == 1
    assert engine.speed == 0
    assert engine.direction == Direction.FORWARD
    assert engine.functions == 0

    engineUpdate: DecodedCommand = DecodedCommand("<l 1 1 200 5>\n".encode())
    engines._command_received(engineUpdate)

    assert engine.speed == 72
    assert engine.direction == Direction.FORWARD
    assert engine.functions == 5
    assert engine.get_function(0) == ActiveState.ON
    assert engine.get_function(1) == ActiveState.OFF
    assert engine.get_function(2) == ActiveState.ON
    assert engine.get_function(3) == ActiveState.OFF

    engineInfo2: DecodedCommand = DecodedCommand("<l 2 2 0 0>\n".encode())
    engines._command_received(engineInfo2)

    assert 2 in engines.engines
    engine2: TrainEngine = engines.engines[2]
    assert engine2.cab == 2
    assert engine2.direction == Direction.REVERSED
    assert engine2.speed == 0
    assert engine2.functions == 0
    assert engine2.get_function(0) == ActiveState.OFF


def test_loco_self_control(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engineIntroduction: DecodedCommand = DecodedCommand("<l 1 1 128 0>\n".encode())
    engines._command_received(engineIntroduction)

    engine: TrainEngine = engines.engines[1]

    engine.set_speed(0, Direction.FORWARD)
    assert mock_ex.last_command_received == "<t 1 1 0 1>"

    engine.set_function(2, ActiveState.ON)
    assert mock_ex.last_command_received == "<F 1 2 1>"


def test_get_engine(mock_ex):
    engines: TrainEngines = TrainEngines(mock_ex)

    engine1: TrainEngine = engines.get_engine(1)

    assert engine1 is not None
    assert engine1 == engines.engines[1]
    assert engine1.functions == 0

    engineInfo: DecodedCommand = DecodedCommand("<l 1 1 128 0>\n".encode())
    engines._command_received(engineInfo)

    assert engine1.direction == Direction.FORWARD
    assert engine1.speed == 0
    assert engine1.functions == 0

    engine2Info: DecodedCommand = DecodedCommand("<l 2 1 128 3>\n".encode())
    engines._command_received(engine2Info)

    assert 2 in engines.engines

    engine2: TrainEngine = engines.get_engine(2)

    assert engine2 == engines.engines[2]
    assert engine2.cab == 2
    assert engine2.direction == Direction.FORWARD
    assert engine2.get_function(0) == ActiveState.ON
    assert engine2.get_function(1) == ActiveState.ON
    assert engine2.get_function(2) == ActiveState.OFF
