# main.py
import yaml
import time
from factory import get_adapter
from db.writer import insert_telemetry

with open("config/devices.yaml") as f:
    config = yaml.safe_load(f)

adapters = []

for device in config["devices"]:
    adapter = get_adapter(device)
    adapter.connect()
    adapters.append(adapter)

while True:
    for adapter in adapters:
        try:
            data = adapter.read()
            if data:
                print(data)
                insert_telemetry(data)
        except Exception as e:
            print("Error:", e)
    time.sleep(2)