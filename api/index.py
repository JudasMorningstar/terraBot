from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from drones import DroneError, get_drone

app = Flask(__name__)
CORS(app)

# Which drone is used is chosen by the DRONE_TYPE env var (default: "sim").
# See api/drones/registry.py.

# Legacy direction names used by the frontend -> (forward, right, up, yaw).
DIRECTIONS = {
    "forward": (1, 0, 0, 0),
    "backward": (-1, 0, 0, 0),
    "left": (0, -1, 0, 0),
    "right": (0, 1, 0, 0),
    "up": (0, 0, 1, 0),
    "down": (0, 0, -1, 0),
    "ccw": (0, 0, 0, -1),
    "cw": (0, 0, 0, 1),
}


def ok(**extra):
    return jsonify({"status": "success", **extra})


def fail(message, code=500):
    return jsonify({"status": "error", "message": message}), code


@app.errorhandler(DroneError)
def handle_drone_error(exc):
    return fail(str(exc), 409)


@app.route("/api/healthchecker", methods=["GET"])
def healthchecker():
    return ok(message="Integrate Flask Framework with Next.js")


@app.route("/api/drone_info", methods=["GET"])
def drone_info():
    return ok(**get_drone().info())


@app.route("/api/takeoff", methods=["POST"])
def takeoff():
    get_drone().takeoff()
    return ok(message="Drone took off")


@app.route("/api/land", methods=["POST"])
def land():
    get_drone().land()
    return ok(message="Drone landed")


@app.route("/api/emergency_stop", methods=["POST"])
def emergency_stop():
    drone = get_drone()
    drone.abort_sequence()
    drone.emergency_stop()
    return ok(message="Motors stopped")


@app.route("/api/drone_status", methods=["GET"])
def drone_status():
    t = get_drone().get_telemetry()
    return ok(
        # Keys the current frontend reads:
        flight_time=t.flight_time,
        battery_level=t.battery,
        speed=t.speed,
        distance=t.distance,
        temperature=t.temperature,
        altitude=t.altitude,
        # Extra fields:
        is_flying=t.is_flying,
        x=t.x,
        y=t.y,
        heading=t.heading,
    )


@app.route("/api/battery", methods=["GET"])
def battery():
    return ok(battery_level=get_drone().get_telemetry().battery)


@app.route("/api/control", methods=["POST"])
def control():
    """Accepts either {"direction": "forward", "speed": 50} or
    {"forward": 0, "right": 0, "up": 0, "yaw": 0} (each -100..100)."""
    body = request.get_json(silent=True) or {}
    drone = get_drone()

    if "direction" in body:
        direction = body["direction"]
        if direction not in DIRECTIONS:
            return fail(f"Unknown direction '{direction}'", 400)
        try:
            speed = float(body.get("speed", 50))
        except (TypeError, ValueError):
            return fail("speed must be a number", 400)
        drone.move(*(axis * speed for axis in DIRECTIONS[direction]))
    else:
        try:
            axes = {k: float(body.get(k, 0)) for k in ("forward", "right", "up", "yaw")}
        except (TypeError, ValueError):
            return fail("Axis values must be numbers", 400)
        drone.move(**axes)

    return ok(message="Control command sent successfully")


@app.route("/api/perform_sequence", methods=["POST"])
def perform_sequence():
    get_drone().start_sequence()
    return ok(message="Sequence started")


@app.route("/api/abort_sequence", methods=["POST"])
def abort_sequence():
    get_drone().abort_sequence()
    return ok(message="Sequence aborted")


@app.route("/api/video_feed")
def video_feed():
    drone = get_drone()

    def generate():
        for frame in drone.frames():
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run()
