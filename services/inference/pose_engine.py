import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import time
class PoseEngine:
    def __init__(self):
        base_options = python.BaseOptions(
            model_asset_path="pose_landmarker_heavy.task"
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)

    def infer(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        # ⚠️ REQUIRED for VIDEO mode
        timestamp_ms = int(time.time() * 1000)

        result = self.detector.detect_for_video(mp_image, timestamp_ms)

        annotated = frame.copy()

        if result.pose_landmarks:
            h, w, _ = frame.shape

            for pose in result.pose_landmarks:
                for lm in pose:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(annotated, (cx, cy), 3, (0, 255, 0), -1)

        return annotated