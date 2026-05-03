import pika
import json

class RabbitMQPublisher:
    def __init__(self, host="localhost", queue="video_events"):
        self.queue = queue

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host)
        )
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, message):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent
            )
        )
        print("📤 Sent to RabbitMQ:", message)