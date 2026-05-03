import pika
import json
import psycopg2
import time
import os
import sys
import threading
import paho.mqtt.client as mqtt
# -------------------------
# Config (from env)
# -------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "video_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "timescaledb"),
    "port": os.getenv("DB_PORT", "5432")
}

VIDEO_QUEUE = "video_events"
MQTT_TOPIC = "industrial/#"


# -------------------------
# DB Connection (with retry)
# -------------------------
def connect_db():
    while True:
        try:
            print("🔌 Connecting to TimescaleDB...")
            conn = psycopg2.connect(**DB_CONFIG)
            print("✅ Connected to DB")
            return conn
        except Exception as e:
            print(f"❌ DB connection failed: {e}")
            time.sleep(5)


# -------------------------
# RabbitMQ Connection (with retry)
# -------------------------
def connect_rabbitmq():
    while True:
        try:
            print("🔌 Connecting to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            print("✅ Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("❌ RabbitMQ not ready, retrying in 5 seconds...")
            time.sleep(5)


# -------------------------
# VIDEO EVENT HANDLER (AMQP)
# -------------------------
def video_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"🎥 Video Event: {data}")

        cur = db_conn.cursor()

        cur.execute("""
            INSERT INTO video_events (time, camera_id, object_type, confidence, bbox, track_id)
            VALUES (NOW(), %s, %s, %s, %s, %s)
        """, (
            data["camera_id"],
            data["object_type"],
            data["confidence"],
            str(data["bbox"]),
            data.get("track_id", "na")
        ))

        db_conn.commit()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Video error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# -------------------------
# TELEMETRY HANDLER (MQTT)
# -------------------------
def mqtt_on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"📡 Telemetry: {data}")

        cur = db_conn.cursor()

        cur.execute("""
            INSERT INTO telemetry (time, device, protocol, metrics)
            VALUES (NOW(), %s, %s, %s)
        """, (
            data.get("device_id"),
            data.get("protocol"),
            json.dumps(data.get("metrics", {}))
        ))

        db_conn.commit()

    except Exception as e:
        print(f"❌ Telemetry error: {e}")

# -------------------------
# MQTT THREAD
# -------------------------
def start_mqtt():
    while True:
        try:
            print("🔌 Connecting to MQTT...")
            client = mqtt.Client()
            client.connect(RABBITMQ_HOST, MQTT_PORT, 60)

            client.on_message = mqtt_on_message
            client.subscribe(MQTT_TOPIC, qos=1)

            print(f"📡 Subscribed to {MQTT_TOPIC}")
            client.loop_forever()

        except Exception as e:
            print(f"❌ MQTT reconnecting: {e}")
            time.sleep(5)

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    print("🚀 Starting ingestion service...")

    db_conn = connect_db()

    # Start MQTT in background
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()

    # AMQP setup
    rabbit_conn = connect_rabbitmq()
    channel = rabbit_conn.channel()

    channel.queue_declare(queue=VIDEO_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=VIDEO_QUEUE,
        on_message_callback=video_callback,
        auto_ack=False
    )

    print("🚀 Waiting for AMQP + MQTT messages...")
    channel.start_consuming()