import json
import paho.mqtt.client as mqtt

class MQTTPublisher:
    def __init__(self, host="localhost", port=1883):
        self.client = mqtt.Client()
        self.client.connect(host, port, 60)

    def publish(self, topic, payload):
        self.client.publish(topic, json.dumps(payload))