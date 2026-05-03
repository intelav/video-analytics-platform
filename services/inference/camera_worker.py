import threading
import time
from yolo_utils import postprocess
import pika
import json
from queue import Queue
from pose_engine import PoseEngine

event_queue = Queue()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='video_events', durable=True)

def publish_event(event):
    channel.basic_publish(
    exchange='',
    routing_key='video_events',
    body=json.dumps(event),
    properties=pika.BasicProperties(
        delivery_mode=2  # 🔥 makes message persistent
    )
)

def start_publisher(event_queue: Queue):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    channel.queue_declare(queue='video_events', durable=True)

    print("📡 RabbitMQ publisher started")

    while True:
        try:
            event = event_queue.get()

            channel.basic_publish(
                exchange='',
                routing_key='video_events',
                body=json.dumps(event),
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )

        except Exception as e:
            print(f"[RabbitMQ ERROR] {e}")
            time.sleep(1)

class CameraWorker:
    def __init__(self, cam_id, camera, inference_engine):
        self.cam_id = cam_id
        self.camera = camera
        self.inference = inference_engine
        self.running = True    
        self.frame = None
        self.lock = threading.Lock()
        self.pose_engine = PoseEngine()

        self.yolo_frame = None
        self.pose_frame = None
        t = threading.Thread(target=self.run, daemon=True)
        t.start()

    def run(self):
        while self.running:
            frame, depth = self.camera.read()
            if frame is None:
                continue

            try:
                preds = self.inference.infer(frame)
            except Exception as e:
                print(f"[ERROR] Inference failed: {e}")
                continue

            annotated, detections = postprocess(preds, frame, depth)
            pose_annotated = self.pose_engine.infer(frame)    
            # publish events (reuse your RabbitMQ)
            for det in detections:
                det["camera_id"] = self.cam_id
                event_queue.put(det)

            with self.lock:
                self.frame = annotated
                self.yolo_frame = annotated
                self.pose_frame = pose_annotated

            time.sleep(0.03)  # throttle

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False        

    def get_yolo_frame(self):
        with self.lock:
            return self.yolo_frame

    def get_pose_frame(self):
        with self.lock:
            return self.pose_frame    