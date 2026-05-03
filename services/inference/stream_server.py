from flask import Flask, Response
import cv2
import threading
import time

app = Flask(__name__)

CAMERAS = {
    "cam1": 0,
    "cam2": 1,
    "cam3": 2,
}

class CameraStream:
    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self.frame = None
        self.lock = threading.Lock()
        self.running = True

        t = threading.Thread(target=self.update, daemon=True)
        t.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            # 🔥 integrate inference here
            # frame = run_inference(frame)

            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame

streams = {}

# initialize once
for name, src in CAMERAS.items():
    streams[name] = CameraStream(src)


def generate(cam_name):
    stream = streams[cam_name]

    while True:
        frame = stream.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes +
               b'\r\n')
        time.sleep(0.03) 

@app.route('/video/<cam_name>')
def video_feed(cam_name):
    if cam_name not in streams:
        return "Camera not found", 404

    return Response(generate(cam_name),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)