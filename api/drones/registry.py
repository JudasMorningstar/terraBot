"""Chooses which drone adapter the server uses (``DRONE_TYPE`` env var)."""
from __future__ import annotations

import os
import threading
from typing import Callable, Dict, Optional

from .base import DroneAdapter, DroneError

DEFAULT_DRONE_TYPE = "sim"


def _make_sim() -> DroneAdapter:
    from .sim import SimulatedDrone

    return SimulatedDrone()


def _make_tello() -> DroneAdapter:
    from .tello import TelloAdapter

    return TelloAdapter()


# Add new adapters here. Factories import lazily so optional dependencies
# (djitellopy, pymavlink...) are only needed when that drone is selected.
ADAPTERS: Dict[str, Callable[[], DroneAdapter]] = {
    "sim": _make_sim,
    "tello": _make_tello,
}

_lock = threading.Lock()
_drone: Optional[DroneAdapter] = None


def get_drone() -> DroneAdapter:
    """Return the process-wide drone, creating and connecting it on first use."""
    global _drone
    with _lock:
        if _drone is None:
            drone_type = os.environ.get("DRONE_TYPE", DEFAULT_DRONE_TYPE).lower()
            factory = ADAPTERS.get(drone_type)
            if factory is None:
                raise DroneError(
                    f"Unknown DRONE_TYPE '{drone_type}'. Available: {', '.join(sorted(ADAPTERS))}"
                )
            drone = factory()
            drone.connect()
            _drone = drone
        return _drone


def reset_drone() -> None:
    """Disconnect and forget the current drone (used by tests)."""
    global _drone
    with _lock:
        if _drone is not None:
            _drone.disconnect()
            _drone = None
