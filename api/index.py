from flask import Flask, Response, jsonify
from flask_cors import CORS
from djitellopy import Tello
import cv2

app = Flask(__name__)
tello = Tello()

CORS(app)


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
    while True:
        tello.connect()
        tello.streamon()
        frame_read = tello.get_frame_read()
        frame = frame_read.frame
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


if __name__ == "__main__":
    app.run()
