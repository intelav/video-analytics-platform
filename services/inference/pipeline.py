from camera import USBCamera, RealSenseCamera
from inference_engine import InferenceEngine
from camera_worker import CameraWorker
from camera_registry import get_camera_config

import tritonclient.grpc as grpcclient
import redis

def build_pipeline():
    cam_config = get_camera_config()

    print("Detected cameras:", cam_config)

    # shared inference engine
    triton_client = grpcclient.InferenceServerClient("localhost:8001")
    redis_client = redis.Redis(host="localhost", port=6379)

    engine = InferenceEngine(triton_client, redis_client)

    workers = {}

    for cam_name, cfg in cam_config.items():
        if cfg["type"] == "realsense":
            cam = RealSenseCamera()
        elif cfg["type"] == "usb":
            cam = USBCamera(cfg["device"])
        else:
            continue

        workers[cam_name] = CameraWorker(cam_name, cam, engine)

    return workers