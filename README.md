# terraBot

An open-source web dashboard for flying drones: live video, telemetry and keyboard control in the browser, on top of a small **drone adapter layer** so the same UI can drive different drones.

It ships with a **built-in simulator**, so you can try everything without any hardware.

| Drone | Status |
|---|---|
| Simulator (`sim`) | Working. The default, needs no hardware |
| DJI / Ryze Tello (`tello`) | Supported through `djitellopy` |
| MAVLink (PX4 / ArduPilot) | Planned |
| ROS 2 / NVIDIA Isaac Sim | Ideas, see [Adding a drone](#adding-a-drone) |

## Quick start (simulator)

You need **Node 18+**, [pnpm](https://pnpm.io) and **Python 3.9+**.

```bash
pnpm install
pip3 install -r requirements.txt
pnpm run dev
```

Open <http://localhost:3000>, press **Launch** (or `e`) and fly with the keys below.

`pnpm run dev` starts both servers: Next.js on port 3000 and the Flask API on port 5328. In development Next.js proxies `/api/*` to Flask (see `next.config.js`).

### Controls

| Key | Action |
|---|---|
| `e` / `q` | Take off / land |
| Arrow keys | Forward, backward, strafe left, strafe right |
| `w` / `s` | Up / down |
| `a` / `d` | Rotate counter-clockwise / clockwise |

Hold a key to keep moving. If commands stop arriving for 1 second, the drone stops by itself. The **Emergency Stop** button cuts the motors immediately (the drone will fall).

## Using a real Tello

1. Install the extra dependency: `pip3 install -r requirements-tello.txt`
2. Connect your computer to the Tello's Wi-Fi network.
3. Start with `DRONE_TYPE=tello`:

```bash
DRONE_TYPE=tello pnpm run dev
```

You can also copy `.env.example` to `.env` and set `DRONE_TYPE` there. Note that while connected to the Tello's Wi-Fi your computer has no internet access, so install dependencies first.

> **Safety:** fly in an open area, keep the drone in sight, and follow your local drone regulations. This project is not a flight-safety system.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `DRONE_TYPE` | `sim` | Which adapter the backend uses (`sim`, `tello`) |
| `NEXT_PUBLIC_API_BASE` | `/api` | Where the frontend finds the API |

## Architecture

```
Browser (Next.js, React, Tailwind, shadcn/ui, Zustand)
   │  HTTP  /api/*          video: MJPEG stream at /api/video_feed
   ▼
Flask API  (api/index.py)        ← routes only, no drone-specific code
   │
   ▼
DroneAdapter interface  (api/drones/base.py)
   ├── SimulatedDrone   (sim.py)
   ├── TelloAdapter     (tello.py)
   └── your adapter…    (registered in registry.py)
```

The frontend and the routes only know the `DroneAdapter` interface. The UI asks `/api/drone_info` which **capabilities** the connected drone has (`video`, `temperature`, `tof_sensor`, `position`) and shows only the matching widgets.

### API

| Endpoint | Description |
|---|---|
| `GET /api/drone_info` | Name, description, capabilities, limits, whether it is simulated |
| `GET /api/drone_status` | Telemetry: battery, altitude, speed, flight time, position… |
| `GET /api/battery` | Battery percentage |
| `POST /api/takeoff`, `POST /api/land` | Take off / land |
| `POST /api/emergency_stop` | Cut the motors immediately |
| `POST /api/control` | `{"direction": "forward", "speed": 50}` or `{"forward": 0, "right": 0, "up": 0, "yaw": 0}` (each -100..100) |
| `POST /api/perform_sequence`, `POST /api/abort_sequence` | Run or abort a scripted flight in the background |
| `GET /api/video_feed` | MJPEG video stream |

Errors return `{"status": "error", "message": "..."}`. A command the drone cannot perform right now (for example taking off twice) returns HTTP 409.

## Adding a drone

1. Create `api/drones/mydrone.py` with a class that extends `DroneAdapter` and implements `connect`, `disconnect`, `takeoff`, `land`, `emergency_stop`, `_send_move`, `get_telemetry` and `frames`. Set `name`, `description` and `capabilities`.
   - `_send_move(forward, right, up, yaw)` receives values already clamped to -100..100 (+forward, +right, +up, +clockwise).
   - `get_telemetry()` returns a `Telemetry`. Use SI units (metres, m/s) and leave unknown fields as `None`.
   - `frames()` yields JPEG bytes.
   - Raise `DroneError` when a command fails or is not allowed.
2. Register it in `api/drones/registry.py`. Import optional dependencies lazily inside the factory, so the other drones keep working without them.
3. Run `DRONE_TYPE=mydrone pnpm run dev`.

The movement watchdog and the scripted-sequence runner come from the base class, and `api/drones/sim.py` is the reference implementation.

## Tests

```bash
pip3 install -r requirements-dev.txt
pnpm run test:api
```

The tests run against the simulator, so they need no hardware.

## Project layout

```
api/            Flask API and drone adapters
  drones/       base.py, registry.py, sim.py, tello.py
app/            Next.js pages (home dashboard; gallery, map and notifications are placeholders)
components/     UI components (drone/ holds the dashboard widgets)
lib/            API client (drone.ts) and Zustand store
tests/          pytest suite
```

## Status and ideas

Early stage. Possible next steps: object detection on the video feed (the EfficientDet model is already in `api/models/`), a MAVLink adapter for PX4 / ArduPilot (which would also cover PX4-based simulators such as Isaac Sim's Pegasus extension), mission planning on the map page, and a media gallery.

The Flask backend needs to run on a machine that can reach the drone, so it is not meant to be deployed to serverless hosting.

## License

No license has been chosen yet. Until one is added, all rights are reserved by default.
