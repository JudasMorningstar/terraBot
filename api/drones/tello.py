"""Adapter for the DJI/Ryze Tello (via djitellopy)."""
from __future__ import annotations

import time
from typing import Iterator

import cv2

from .base import (
    CAP_TEMPERATURE,
    CAP_TOF_SENSOR,
    CAP_VIDEO,
    DroneAdapter,
    DroneError,
    Telemetry,
)


class TelloAdapter(DroneAdapter):
    name = "DJI Tello"
    capabilities = frozenset({CAP_VIDEO, CAP_TOF_SENSOR, CAP_TEMPERATURE})

    FRAME_INTERVAL = 1 / 30

    def __init__(self) -> None:
        super().__init__()
        # Imported lazily so the simulator works without djitellopy installed.
        from djitellopy import Tello

        self._tello = Tello()
        self._connected = False
        self._frame_reader = None

    def connect(self) -> None:
        if self._connected:
            return
        try:
            self._tello.connect()
            self._tello.streamon()
            self._frame_reader = self._tello.get_frame_read()
        except Exception as exc:  # djitellopy raises plain Exceptions
            raise DroneError(f"Could not connect to Tello: {exc}") from exc
        self._connected = True

    def disconnect(self) -> None:
        self._stop_watchdog()
        if not self._connected:
            return
        try:
            self._tello.streamoff()
            self._tello.end()
        finally:
            self._connected = False
            self._frame_reader = None

    def _require_connection(self) -> None:
        if not self._connected:
            raise DroneError("Drone is not connected")

    def takeoff(self) -> None:
        self._require_connection()
        try:
            self._tello.takeoff()
        except Exception as exc:
            raise DroneError(f"Takeoff failed: {exc}") from exc

    def land(self) -> None:
        self._require_connection()
        try:
            self._tello.land()
        except Exception as exc:
            raise DroneError(f"Landing failed: {exc}") from exc

    def emergency_stop(self) -> None:
        self._require_connection()
        self._tello.emergency()

    def _send_move(self, forward: int, right: int, up: int, yaw: int) -> None:
        self._require_connection()
        # djitellopy order: left_right, forward_backward, up_down, yaw
        self._tello.send_rc_control(right, forward, up, yaw)

    def get_telemetry(self) -> Telemetry:
        self._require_connection()
        try:
            t = self._tello
            return Telemetry(
                battery=t.get_battery(),
                altitude=t.get_height() / 100,  # cm -> m
                speed=t.get_speed_x(),
                flight_time=t.get_flight_time(),
                temperature=t.get_temperature(),
                distance=t.get_distance_tof() / 100,  # cm -> m
                is_flying=bool(t.is_flying),
            )
        except Exception as exc:
            raise DroneError(f"Could not read telemetry: {exc}") from exc

    def frames(self) -> Iterator[bytes]:
        self._require_connection()
        reader = self._frame_reader
        while self._connected:
            frame = reader.frame
            # Same colour handling as the original implementation.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ok, buffer = cv2.imencode(".jpg", frame)
            if ok:
                yield buffer.tobytes()
            time.sleep(self.FRAME_INTERVAL)
