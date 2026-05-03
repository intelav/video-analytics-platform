import yaml
import time
from factory import get_adapter
from common.mqtt_publisher import MQTTPublisher
from common.rabbitmq_publisher import RabbitMQPublisher

with open("config/devices.yaml") as f:
    config = yaml.safe_load(f)

publisher = MQTTPublisher(host="localhost", port=1883)
#publisher = RabbitMQPublisher(host="localhost", queue="video_events")

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
                topic = f"industrial/{data['protocol']}/{data['device_id']}"
                publisher.publish(topic, data)
                print("Published:", topic, data)
        except Exception as e:
            print("Error:", e)

    time.sleep(2)