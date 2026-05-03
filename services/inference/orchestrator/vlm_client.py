import requests
import base64
import cv2


class VLMClient:
    def __init__(self, endpoint="http://localhost:8000/generate"):
        self.endpoint = endpoint

    def encode_image(self, frame):
        _, buffer = cv2.imencode(".jpg", frame)
        return base64.b64encode(buffer).decode("utf-8")

    def infer(self, frame, prompt):
        img_b64 = self.encode_image(frame)

        payload = {
            "image": img_b64,
            "prompt": prompt,
            "max_tokens": 128
        }

        response = requests.post(self.endpoint, json=payload)
        return response.json().get("text", "")