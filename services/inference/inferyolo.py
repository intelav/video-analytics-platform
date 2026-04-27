import tritonclient.http as httpclient
import tritonclient.grpc as grpcclient
import numpy as np
import cv2
import pyrealsense2 as rs
import json
import paho.mqtt.client as mqtt
import pickle
import time
import redis
import hashlib
import pika
# -----------------------------
# Redis Cache
# -----------------------------
r = redis.Redis(host="localhost", port=6379)

def get_cache(inp):
    key = hashlib.md5(inp.tobytes()).hexdigest()
    val = r.get(key)
    return key, val

def set_cache(key, val):
    r.setex(key, 60, val)

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
# -----------------------------
# Triton client
# -----------------------------
clientrpc = grpcclient.InferenceServerClient("localhost:8001")

# -----------------------------
# RealSense setup
# -----------------------------
pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

pipeline.start(config)
align = rs.align(rs.stream.color)

with open("coco.names", "r") as f:
    CLASSES = [line.strip() for line in f.readlines()]

# -----------------------------
# Preprocess
# -----------------------------
def preprocess(frame):
    img = cv2.resize(frame, (640, 640))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))  # HWC → CHW
    return img

# -----------------------------
# Postprocess
# -----------------------------
def postprocess(preds, frame, depth=None, conf_thres=0.25, iou_thres=0.45):
    detections = []
    output = preds[0]

    boxes = output[:4, :].T
    scores = output[4:, :].T

    class_ids = np.argmax(scores, axis=1)
    confidences = np.max(scores, axis=1)

    mask = confidences > conf_thres
    boxes = boxes[mask]
    confidences = confidences[mask]
    class_ids = class_ids[mask]

    if len(boxes) == 0:
        return frame, detections

    h, w = frame.shape[:2]
    scale_x = w / 640
    scale_y = h / 640

    boxes_xyxy = []

    for box in boxes:
        cx, cy, bw, bh = box
        x1 = int((cx - bw/2) * scale_x)
        y1 = int((cy - bh/2) * scale_y)
        x2 = int((cx + bw/2) * scale_x)
        y2 = int((cy + bh/2) * scale_y)
        boxes_xyxy.append([x1, y1, x2, y2])

    indices = cv2.dnn.NMSBoxes(
        boxes_xyxy,
        confidences.tolist(),
        conf_thres,
        iou_thres
    )

    if len(indices) == 0:
        return frame, detections

    for i in indices.flatten():
        x1, y1, x2, y2 = boxes_xyxy[i]
        conf = confidences[i]
        cls = class_ids[i]

        label = CLASSES[cls]

        detection = {
            "camera_id": "cam-1",
            "object_type": str(label),
            "confidence": float(conf),
            "bbox": [int(x1), int(y1), int(x2), int(y2)],
            "track_id": "na"
        }

        if depth is not None:
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            if 0 <= cx < depth.shape[1] and 0 <= cy < depth.shape[0]:
                distance = float(depth[cy, cx] * 0.001)
                label += f" {distance:.2f}m"

        label += f" {conf:.2f}"
        detections.append(detection)

        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(frame, label, (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0,255,0), 1)

    return frame, detections

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        start_time = time.time()

        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not depth_frame:
            continue
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        depth = np.asanyarray(depth_frame.get_data())

        inp = preprocess(frame)
        inp = np.expand_dims(inp, axis=0)

        # ✅ IMPORTANT: hash raw numpy input (NOT Triton input object)
        key, cached = get_cache(inp)

        if cached:
            print("🔥 Cache HIT")
            preds = pickle.loads(cached)

        else:
            print("❄️ Cache MISS → Triton inference")

            inputs = [grpcclient.InferInput("images", inp.shape, "FP32")]
            inputs[0].set_data_from_numpy(inp)

            outputs = [grpcclient.InferRequestedOutput("output0")]

            result = clientrpc.infer("yolov8", inputs, outputs=outputs)
            preds = result.as_numpy("output0")

            set_cache(key, pickle.dumps(preds))

        # Postprocess
        frame, detections = postprocess(preds, frame, depth=depth)

        # MQTT publish
        for det in detections:
            publish_event(det)

        # Display
        cv2.imshow("Detections", frame)

        latency = time.time() - start_time
        print(f"⏱ Latency: {latency:.4f}s")

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()