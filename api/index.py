from flask import Flask
from flask_cors import CORS
from djitellopy import Tello


app = Flask(__name__)
tello = Tello()
CORS(app)

@app.route('/takeoff', methods=['POST'])
def takeoff():
    tello.connect()
    tello.streamon()
    tello.takeoff()
    return {"status": "success", "message": "Drone took off"}

@app.route('/land', methods=['POST'])
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
        frame_read = tello.get_frame_read()
        frame = frame_read.frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run()