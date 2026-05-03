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

def generate(cam_name, mode="yolo"):
    worker = workers[cam_name]

    while True:
        if mode == "pose":
            frame = worker.get_pose_frame()
        else:
            frame = worker.get_yolo_frame()

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
    return {
    "cam1": {"yolo": True, "pose": True},
    "cam2": {"yolo": True, "pose": False}
    }

@app.route('/video_pose/<cam_name>')
def stream_pose(cam_name):
    if cam_name not in workers:
        return "Camera not found", 404

    return Response(generate(cam_name, mode="pose"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def shutdown(sig, frame):
    print("Shutting down...")
    for w in workers.values():
        w.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)

if __name__ == "__main__":
    print("🚀 Starting streaming server...")
    app.run(host="0.0.0.0", port=5000, threaded=True)