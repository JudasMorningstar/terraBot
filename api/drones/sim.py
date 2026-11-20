"""Simulated drone: no hardware or extra dependencies (just Pillow).

Runs a small physics loop on a background thread and renders a synthetic
top-down camera view, so the whole dashboard can be tried without a drone.
"""
from __future__ import annotations

import io
import math
import threading
import time
from typing import Callable, Iterator, Optional

from PIL import Image, ImageDraw

from .base import (
    CAP_POSITION,
    CAP_TEMPERATURE,
    CAP_VIDEO,
    DroneAdapter,
    DroneError,
    Telemetry,
)

# --- physics / battery constants ---------------------------------------
MAX_SPEED = 2.0  # m/s at full stick
MAX_VERTICAL_SPEED = 1.0  # m/s
MAX_YAW_RATE = 90.0  # deg/s
HOVER_ALTITUDE = 1.2  # m reached after takeoff
LANDING_SPEED = 0.8  # m/s
MAX_ALTITUDE = 10.0
MIN_FLYING_ALTITUDE = 0.3

BATTERY_DRAIN_FLYING = 0.12  # percent / s  (~14 min of flight)
BATTERY_DRAIN_IDLE = 0.005
LOW_BATTERY_AUTOLAND = 5.0  # percent

# --- video constants ---------------------------------------------------
FRAME_SIZE = (640, 480)
PIXELS_PER_METRE = 24
GRID_METRES = 2
FRAME_INTERVAL = 1 / 20

# Moving scenery for a future detection pipeline to find:
# (label, colour, size_m (w, h), orbit_centre (x, y), orbit_radius, period_s)
SCENE_OBJECTS = (
    ("person", (230, 90, 70), (0.6, 0.6), (4.0, 3.0), 2.5, 24.0),
    ("car", (70, 120, 230), (2.2, 1.1), (-6.0, 2.0), 3.0, 40.0),
    ("person", (240, 190, 60), (0.6, 0.6), (1.0, -6.0), 1.5, 15.0),
)


class SimulatedDrone(DroneAdapter):
    name = "Simulator"
    description = "A virtual drone for trying the dashboard without any hardware."
    simulated = True
    max_speed = MAX_SPEED
    max_altitude = MAX_ALTITUDE
    capabilities = frozenset({CAP_VIDEO, CAP_POSITION, CAP_TEMPERATURE})

    def __init__(self, autostart: bool = True) -> None:
        super().__init__()
        self._autostart = autostart
        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._connected = False
        self._reset_state()

    def _reset_state(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.altitude = 0.0
        self.heading = 0.0
        self.battery = 100.0
        self.flight_time = 0.0
        self.speed = 0.0
        self.sim_time = 0.0
        self._state = "grounded"  # grounded | flying | landing
        self._stick = (0, 0, 0, 0)  # forward, right, up, yaw
        self.warning = ""

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def connect(self) -> None:
        with self._lock:
            if self._connected:
                return
            self._connected = True
        if self._autostart:
            self._running.set()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def disconnect(self) -> None:
        self._stop_watchdog()
        self._running.clear()
        thread = self._thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=1)
        self._thread = None
        with self._lock:
            self._connected = False

    def _require_connection(self) -> None:
        if not self._connected:
            raise DroneError("Drone is not connected")

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    def takeoff(self) -> None:
        self._require_connection()
        with self._lock:
            if self._state == "flying":
                raise DroneError("Drone is already flying")
            if self._state == "landing":
                raise DroneError("Drone is landing")
            if self.battery <= LOW_BATTERY_AUTOLAND:
                raise DroneError("Battery too low to take off")
            self._state = "flying"
            self.warning = ""
        self._wait_until(lambda: self.altitude >= HOVER_ALTITUDE - 0.05, timeout=10)

    def land(self) -> None:
        self._require_connection()
        with self._lock:
            if self._state == "grounded":
                raise DroneError("Drone is not flying")
            self._state = "landing"
            self._stick = (0, 0, 0, 0)
        self._wait_until(lambda: self._state == "grounded", timeout=15)

    def emergency_stop(self) -> None:
        self._require_connection()
        with self._lock:
            self._state = "grounded"
            self.altitude = 0.0
            self.speed = 0.0
            self._stick = (0, 0, 0, 0)
            self.warning = "Emergency stop"

    def _send_move(self, forward: int, right: int, up: int, yaw: int) -> None:
        self._require_connection()
        with self._lock:
            # Sticks are ignored unless airborne (as on a real drone).
            self._stick = (forward, right, up, yaw) if self._state == "flying" else (0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------
    def _wait_until(self, condition: Callable[[], bool], timeout: float) -> None:
        """Block until ``condition`` holds. Steps the physics itself if no thread runs."""
        deadline = time.monotonic() + timeout
        while not condition():
            if time.monotonic() > deadline:
                raise DroneError("Timed out waiting for the drone")
            if self._thread is None:
                self.step(0.05)
            else:
                time.sleep(0.02)

    def _loop(self) -> None:
        last = time.monotonic()
        while self._running.is_set():
            time.sleep(0.05)
            now = time.monotonic()
            self.step(now - last)
            last = now

    def step(self, dt: float) -> None:
        """Advance the simulation by ``dt`` seconds."""
        with self._lock:
            self.sim_time += dt
            forward, right, up, yaw = self._stick

            if self._state == "flying":
                self.flight_time += dt
                self.heading = (self.heading + yaw / 100 * MAX_YAW_RATE * dt) % 360
                h = math.radians(self.heading)
                v_f = forward / 100 * MAX_SPEED
                v_r = right / 100 * MAX_SPEED
                self.x += (v_f * math.sin(h) + v_r * math.cos(h)) * dt
                self.y += (v_f * math.cos(h) - v_r * math.sin(h)) * dt
                self.speed = v_f

                if up:
                    self.altitude += up / 100 * MAX_VERTICAL_SPEED * dt
                elif self.altitude < HOVER_ALTITUDE:
                    # Climb to hover height after takeoff.
                    self.altitude = min(HOVER_ALTITUDE, self.altitude + MAX_VERTICAL_SPEED * dt)
                self.altitude = max(MIN_FLYING_ALTITUDE, min(MAX_ALTITUDE, self.altitude))
                self.battery -= BATTERY_DRAIN_FLYING * dt

                if self.battery <= LOW_BATTERY_AUTOLAND:
                    self.warning = "Low battery: landing automatically"
                    self._state = "landing"
                    self._stick = (0, 0, 0, 0)

            elif self._state == "landing":
                self.speed = 0.0
                self.altitude = max(0.0, self.altitude - LANDING_SPEED * dt)
                self.battery -= BATTERY_DRAIN_FLYING * dt
                if self.altitude <= 0.0:
                    self._state = "grounded"
            else:
                self.speed = 0.0
                self.battery -= BATTERY_DRAIN_IDLE * dt

            self.battery = max(0.0, self.battery)

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------
    def get_telemetry(self) -> Telemetry:
        self._require_connection()
        with self._lock:
            return Telemetry(
                battery=int(round(self.battery)),
                altitude=round(self.altitude, 2),
                speed=round(self.speed, 2),
                flight_time=int(self.flight_time),
                temperature=round(25 + 0.1 * min(self.flight_time, 300) / 10, 1),
                distance=None,
                is_flying=self._state != "grounded",
                x=round(self.x, 2),
                y=round(self.y, 2),
                heading=round(self.heading, 1),
            )

    # ------------------------------------------------------------------
    # Synthetic video
    # ------------------------------------------------------------------
    def render_frame(self) -> bytes:
        """Render the current top-down camera view as a JPEG."""
        with self._lock:
            x, y, heading, alt = self.x, self.y, self.heading, self.altitude
            sim_time, warning = self.sim_time, self.warning
            battery, state = self.battery, self._state

        width, height = FRAME_SIZE
        cx, cy = width // 2, height // 2
        scale = PIXELS_PER_METRE
        img = Image.new("RGB", FRAME_SIZE, (46, 94, 58))
        draw = ImageDraw.Draw(img)

        def to_px(wx: float, wy: float) -> tuple:
            return cx + (wx - x) * scale, cy - (wy - y) * scale

        # Ground grid, scrolling with the drone.
        span_x = width / scale / 2 + GRID_METRES
        span_y = height / scale / 2 + GRID_METRES
        gx = math.floor((x - span_x) / GRID_METRES) * GRID_METRES
        while gx <= x + span_x:
            px, _ = to_px(gx, y)
            draw.line([(px, 0), (px, height)], fill=(58, 112, 70), width=1)
            gx += GRID_METRES
        gy = math.floor((y - span_y) / GRID_METRES) * GRID_METRES
        while gy <= y + span_y:
            _, py = to_px(x, gy)
            draw.line([(0, py), (width, py)], fill=(58, 112, 70), width=1)
            gy += GRID_METRES

        # Moving objects.
        for label, colour, (w, h), (ox, oy), radius, period in SCENE_OBJECTS:
            angle = 2 * math.pi * sim_time / period
            wx, wy = ox + radius * math.cos(angle), oy + radius * math.sin(angle)
            px, py = to_px(wx, wy)
            hw, hh = w * scale / 2, h * scale / 2
            draw.rectangle([px - hw, py - hh, px + hw, py + hh], fill=colour, outline=(255, 255, 255))
            draw.text((px - hw, py - hh - 12), label, fill=(255, 255, 255))

        # Drone marker (triangle pointing along the heading).
        h = math.radians(heading)
        pts = [(0, -14), (-9, 10), (9, 10)]
        rotated = [
            (cx + px * math.cos(h) - py * math.sin(h), cy + px * math.sin(h) + py * math.cos(h))
            for px, py in pts
        ]
        draw.polygon(rotated, fill=(255, 255, 255), outline=(0, 0, 0))

        # HUD.
        draw.rectangle([0, 0, width, 22], fill=(0, 0, 0))
        draw.text(
            (6, 5),
            f"SIMULATOR  {state.upper()}  ALT {alt:.1f}m  HDG {heading:03.0f}  BAT {battery:.0f}%",
            fill=(255, 255, 255),
        )
        if warning:
            draw.text((6, height - 18), warning, fill=(255, 200, 0))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return buf.getvalue()

    def frames(self) -> Iterator[bytes]:
        self._require_connection()
        while self._connected:
            yield self.render_frame()
            time.sleep(FRAME_INTERVAL)
