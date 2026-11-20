"""Drone adapter interface.

Every supported drone (simulator, Tello, MAVLink, ...) implements
``DroneAdapter``. The Flask routes and the frontend only ever talk to this
interface, so adding a new drone never requires touching them.
"""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Iterator, Optional, Sequence, Tuple

# Capability flags an adapter may advertise (used by the UI to hide features).
CAP_VIDEO = "video"
CAP_TOF_SENSOR = "tof_sensor"
CAP_POSITION = "position"
CAP_TEMPERATURE = "temperature"

# (forward, right, up, yaw, duration_seconds)
SequenceStep = Tuple[int, int, int, int, float]

DEFAULT_SEQUENCE: Sequence[SequenceStep] = (
    (50, 0, 0, 0, 2.0),
    (0, 0, 0, 60, 2.0),
    (50, 0, 0, 0, 2.0),
    (0, 0, 0, 50, 2.0),
    (50, 0, 0, 0, 2.0),
)


class DroneError(Exception):
    """Raised when a command cannot be performed (bad state, link lost...)."""


@dataclass
class Telemetry:
    battery: Optional[int] = None  # percent
    altitude: Optional[float] = None  # metres above takeoff point
    speed: Optional[float] = None  # forward speed, m/s
    flight_time: Optional[float] = None  # seconds
    temperature: Optional[float] = None  # degrees C
    distance: Optional[float] = None  # time-of-flight distance, metres
    is_flying: bool = False
    x: Optional[float] = None  # metres east of the takeoff point
    y: Optional[float] = None  # metres north of the takeoff point
    heading: Optional[float] = None  # degrees clockwise from north

    def to_dict(self) -> dict:
        return asdict(self)


def clamp_axis(value: float) -> int:
    """Clamp a stick value to the normalised -100..100 range."""
    return int(max(-100, min(100, value)))


class DroneAdapter(ABC):
    """Common interface for all drones."""

    name: str = "drone"
    description: str = ""
    capabilities: frozenset = frozenset()
    simulated: bool = False
    # Published limits shown in the UI; None = unknown / not shown.
    max_speed: Optional[float] = None  # m/s
    max_altitude: Optional[float] = None  # m

    # If no move() arrives for this long, the drone is told to stop. This
    # stops a drone running away when a key-up / network packet is lost.
    MOVE_TIMEOUT = 1.0

    def __init__(self) -> None:
        self._last_move = 0.0
        self._moving = False
        self._watchdog_stop = threading.Event()
        self._watchdog: Optional[threading.Thread] = None
        self._move_lock = threading.Lock()
        self._sequence_thread: Optional[threading.Thread] = None
        self._sequence_abort = threading.Event()

    # ------------------------------------------------------------------
    # To implement per drone
    # ------------------------------------------------------------------
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def takeoff(self) -> None: ...

    @abstractmethod
    def land(self) -> None: ...

    @abstractmethod
    def emergency_stop(self) -> None:
        """Cut motors immediately (the drone will fall)."""

    @abstractmethod
    def _send_move(self, forward: int, right: int, up: int, yaw: int) -> None:
        """Apply already-clamped stick values (-100..100)."""

    @abstractmethod
    def get_telemetry(self) -> Telemetry: ...

    @abstractmethod
    def frames(self) -> Iterator[bytes]:
        """Yield JPEG-encoded video frames, forever (or until the client leaves)."""

    # ------------------------------------------------------------------
    # Shared behaviour
    # ------------------------------------------------------------------
    def move(self, forward: float = 0, right: float = 0, up: float = 0, yaw: float = 0) -> None:
        """Set stick values, each -100..100 (+forward, +right, +up, +clockwise)."""
        values = [clamp_axis(v) for v in (forward, right, up, yaw)]
        with self._move_lock:
            self._send_move(*values)
            self._moving = any(values)
            self._last_move = time.monotonic()
            self._ensure_watchdog()

    def stop(self) -> None:
        self.move(0, 0, 0, 0)

    def _ensure_watchdog(self) -> None:
        if self._watchdog and self._watchdog.is_alive():
            return
        self._watchdog_stop.clear()
        self._watchdog = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog.start()

    def _watchdog_loop(self) -> None:
        while not self._watchdog_stop.wait(0.1):
            with self._move_lock:
                if self._moving and time.monotonic() - self._last_move > self.MOVE_TIMEOUT:
                    try:
                        self._send_move(0, 0, 0, 0)
                    finally:
                        self._moving = False

    def _stop_watchdog(self) -> None:
        self._watchdog_stop.set()

    # --- scripted sequences (non-blocking, abortable) -------------------
    @property
    def sequence_running(self) -> bool:
        return bool(self._sequence_thread and self._sequence_thread.is_alive())

    def start_sequence(self, steps: Sequence[SequenceStep] = DEFAULT_SEQUENCE) -> None:
        if self.sequence_running:
            raise DroneError("A sequence is already running")
        self._sequence_abort.clear()
        self._sequence_thread = threading.Thread(
            target=self._run_sequence, args=(list(steps),), daemon=True
        )
        self._sequence_thread.start()

    def abort_sequence(self) -> None:
        self._sequence_abort.set()

    def _run_sequence(self, steps: Sequence[SequenceStep]) -> None:
        try:
            self.takeoff()
            for forward, right, up, yaw, duration in steps:
                end = time.monotonic() + duration
                while time.monotonic() < end:
                    if self._sequence_abort.is_set():
                        return
                    self.move(forward, right, up, yaw)  # keeps watchdog fed
                    time.sleep(0.1)
            self.stop()
        except DroneError:
            pass
        finally:
            try:
                self.stop()
                self.land()
            except DroneError:
                pass

    # ------------------------------------------------------------------
    def info(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": sorted(self.capabilities),
            "max_speed": self.max_speed,
            "max_altitude": self.max_altitude,
            "simulated": self.simulated,
        }
