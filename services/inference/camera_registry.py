import pyrealsense2 as rs

def detect_realsense():
    try:
        ctx = rs.context()
        devices = ctx.query_devices()
        return len(devices) > 0
    except Exception as e:
        print(f"[WARN] RealSense detection failed: {e}")
        return False


def get_camera_config():
    """
    Deterministic camera configuration.
    No probing. No OpenCV scanning.
    """

    config = {}

    # -----------------------------
    # RealSense (single logical camera)
    # -----------------------------
    if detect_realsense():
        config["cam1"] = {
            "type": "realsense",
            "name": "Intel RealSense"
        }

    # -----------------------------
    # USB Cameras (manual mapping)
    # -----------------------------
    # Based on your system:
    # /dev/video6 → Logitech webcam (valid)
    # /dev/video7 → ignore (duplicate/metadata)

    config["cam2"] = {
        "type": "usb",
        "device": 6,
        "name": "USB Webcam"
    }

    return config