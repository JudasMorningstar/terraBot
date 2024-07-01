from flask import Flask, Response, jsonify
from flask_cors import CORS
from djitellopy import Tello
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from time import sleep

app = Flask(__name__)
tello = Tello()

CORS(app)

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Load model
model_path = 'api/models/efficientdet_lite0.tflite'
options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO)
detector = ObjectDetector.create_from_options(options)


@app.route('/api/takeoff', methods=['POST'])
def takeoff():
    tello.connect()
    tello.streamon()
    tello.takeoff()
    return {"status": "success", "message": "Drone took off"}


@app.route('/api/land', methods=['POST'])
def land():
    tello.land()
    tello.streamoff()
    tello.end()

    return {"status": "success", "message": "Drone landed"}


@app.route("/api/healthchecker", methods=["GET"])
def healthchecker():
    return {"status": "success", "message": "Integrate Flask Framework with Next.js"}


def generate_frames():
    tello.connect()
    tello.streamon()
    while True:
        frame_read = tello.get_frame_read()
        frame = frame_read.frame
        # Convert the frame from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/api/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/drone_status', methods=['GET'])
def drone_status():
    try:
        if not tello.connect():
            tello.connect()

        # Gather information from the drone
        flight_time = tello.get_flight_time()
        battery_level = tello.get_battery()
        speed = tello.get_speed_x()
        distance = tello.get_distance_tof()
        temperature = tello.get_temperature()
        altitude = tello.get_height()

        return jsonify({
            'status': 'success',
            'flight_time': flight_time,
            'battery_level': battery_level,
            'speed': speed,
            'distance': distance,
            'temperature': temperature,
            'altitude': altitude
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/api/perform_sequence', methods=['POST'])
def perform_sequence():
    try:
        if not tello.connect():
            tello.connect()

        tello.takeoff()
        sleep(2)
        # move forward
        tello.send_rc_control(0, 50, 0, 0)
        sleep(2)
        # rotate 90 degrees
        tello.send_rc_control(0, 0, 0, 60)
        sleep(2)
        # move forward
        tello.send_rc_control(0, 50, 0, 0)
        sleep(2)
        # rotate 90 degrees
        tello.send_rc_control(0, 0, 0, 50)
        sleep(2)
        # move forward
        tello.send_rc_control(0, 50, 0, 0)
        sleep(2)
        # stop
        tello.send_rc_control(0, 0, 0, 0)
        tello.land()

        return jsonify({
            'status': 'success',
            'message': 'Sequence completed successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/control', methods=['POST'])
def control():
    try:
        if not tello.connect():
            tello.connect()

        direction = request.json.get("direction")
        speed = request.json.get("speed", 50)

        control_values = {
            "forward": (speed, 0, 0, 0),
            "backward": (-speed, 0, 0, 0),
            "left": (0, 0, 0, -speed),
            "right": (0, 0, 0, speed),
            "up": (0, 0, speed, 0),
            "down": (0, 0, -speed, 0),
            "cw": (0, -speed, 0, 0),
            "ccw": (0, speed, 0, 0),
        }

        control_values = control_values.get(direction, (0, 0, 0, 0))
        tello.send_rc_control(*control_values)

        return jsonify({"status": "success", "message": "Control command sent successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run()
