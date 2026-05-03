from flask import Flask, Response
import cv2
from flask_cors import CORS
import time
import signal
import sys
from pipeline import build_pipeline
import threading
from camera_worker import start_publisher,event_queue

app = Flask(__name__)
CORS(app) 
workers = build_pipeline()

threading.Thread(
    target=start_publisher,
    args=(event_queue,),
    daemon=True
).start()

def generate(cam_name):
    worker = workers[cam_name]

    while True:
        frame = worker.get_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        _, buffer = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() +
               b'\r\n')


@app.route('/video/<cam_name>')
def stream(cam_name):
    if cam_name not in workers:
        return "Camera not found", 404

    return Response(generate(cam_name),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cameras')
def list_cameras():
    return list(workers.keys())

def shutdown(sig, frame):
    print("Shutting down...")
    for w in workers.values():
        w.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)

if __name__ == "__main__":
    print("🚀 Starting streaming server...")
    app.run(host="0.0.0.0", port=5000, threaded=True)