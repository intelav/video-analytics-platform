import cv2
import pyrealsense2 as rs
import numpy as np

class BaseCamera:
    def read(self):
        raise NotImplementedError


class USBCamera(BaseCamera):
    def __init__(self, device_id):
        self.cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        return frame, None  # no depth


class RealSenseCamera(BaseCamera):
    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)

    def read(self):
        frames = self.pipeline.wait_for_frames()
        aligned = self.align.process(frames)

        color = aligned.get_color_frame()
        depth = aligned.get_depth_frame()

        if not color:
            return None, None

        frame = np.asanyarray(color.get_data())
        depth_np = np.asanyarray(depth.get_data()) if depth else None

        return frame, depth_np
        
class RTSPCamera(BaseCamera):
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)

    def read(self):
        ret, frame = self.cap.read()
        return frame, None        