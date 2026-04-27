import pika
import json
import psycopg2
import time
import os
import sys

# -------------------------
# Config (from env)
# -------------------------
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "video_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "timescaledb"),
    "port": os.getenv("DB_PORT", "5432")
}

QUEUE_NAME = "video_events"


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
# Callback (consume message)
# -------------------------
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        print(f"📥 Received event: {data}")

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

        print("✅ Inserted into DB")

        # Acknowledge ONLY after success
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Error processing message: {e}")

        # Reject message (optional: requeue=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":

    print("🚀 Starting ingestion service...")

    # Connect DB
    db_conn = connect_db()

    # Connect RabbitMQ
    rabbit_conn = connect_rabbitmq()
    channel = rabbit_conn.channel()

    # Declare queue (safe if already exists)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Fair dispatch (avoid overload)
    channel.basic_qos(prefetch_count=1)

    # Start consuming
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False   # IMPORTANT
    )

    print("🚀 Waiting for messages...")
    channel.start_consuming()