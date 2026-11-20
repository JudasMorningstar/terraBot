import time

import pytest

from drones.base import DroneError
from drones.sim import HOVER_ALTITUDE, SimulatedDrone


@pytest.fixture
def drone():
    """Simulator driven manually (no background thread) for deterministic tests."""
    d = SimulatedDrone(autostart=False)
    d.connect()
    yield d
    d.disconnect()


def run(drone, seconds, dt=0.05):
    for _ in range(int(seconds / dt)):
        drone.step(dt)


def test_requires_connection():
    d = SimulatedDrone(autostart=False)
    with pytest.raises(DroneError):
        d.takeoff()


def test_takeoff_and_land(drone):
    drone.takeoff()
    t = drone.get_telemetry()
    assert t.is_flying and t.altitude == pytest.approx(HOVER_ALTITUDE, abs=0.1)
    drone.land()
    t = drone.get_telemetry()
    assert not t.is_flying and t.altitude == 0


def test_invalid_state_errors(drone):
    with pytest.raises(DroneError):
        drone.land()
    drone.takeoff()
    with pytest.raises(DroneError):
        drone.takeoff()


def test_forward_moves_north_and_right_moves_east(drone):
    drone.takeoff()
    drone.move(forward=100)
    run(drone, 1)
    t = drone.get_telemetry()
    assert t.y == pytest.approx(2.0, abs=0.1) and t.x == pytest.approx(0, abs=0.01)
    drone.move(right=100)
    run(drone, 1)
    t = drone.get_telemetry()
    assert t.x == pytest.approx(2.0, abs=0.1)


def test_yaw_rotates_and_forward_follows_heading(drone):
    drone.takeoff()
    drone.move(yaw=100)
    run(drone, 1)  # 90 degrees clockwise -> facing east
    assert drone.get_telemetry().heading == pytest.approx(90, abs=2)
    drone.move(forward=100)
    run(drone, 1)
    assert drone.get_telemetry().x == pytest.approx(2.0, abs=0.15)


def test_axes_are_clamped(drone):
    drone.takeoff()
    drone.move(forward=1000)
    run(drone, 1)
    assert drone.get_telemetry().y == pytest.approx(2.0, abs=0.1)  # not 20 m


def test_sticks_ignored_on_the_ground(drone):
    drone.move(forward=100)
    run(drone, 1)
    assert drone.get_telemetry().y == 0


def test_battery_drains_and_low_battery_autolands(drone):
    drone.takeoff()
    drone.battery = 5.5
    run(drone, 10)
    t = drone.get_telemetry()
    assert not t.is_flying
    assert "battery" in drone.warning.lower()
    with pytest.raises(DroneError):
        drone.takeoff()


def test_emergency_stop(drone):
    drone.takeoff()
    drone.emergency_stop()
    t = drone.get_telemetry()
    assert not t.is_flying and t.altitude == 0


def test_watchdog_stops_drone_when_commands_stop(drone):
    drone.MOVE_TIMEOUT = 0.2
    drone.takeoff()
    drone.move(forward=100)
    time.sleep(0.5)
    assert drone._stick == (0, 0, 0, 0)


def test_video_frame_is_jpeg(drone):
    assert drone.render_frame()[:2] == b"\xff\xd8"


def test_sequence_runs_and_can_be_aborted():
    d = SimulatedDrone()  # threaded
    d.connect()
    try:
        d.start_sequence([(50, 0, 0, 0, 5.0)])
        time.sleep(1.5)
        assert d.sequence_running and d.get_telemetry().is_flying
        with pytest.raises(DroneError):
            d.start_sequence()
        d.abort_sequence()
        d._sequence_thread.join(timeout=10)
        assert not d.sequence_running and not d.get_telemetry().is_flying
    finally:
        d.disconnect()
