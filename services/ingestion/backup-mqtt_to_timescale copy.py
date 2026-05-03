import json
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import os
# -----------------------------
# DB CONNECTION (retry logic)
# -----------------------------
def connect_db():
    while True:
        try:
            conn = psycopg2.connect(
                host="timescaledb",   # 🔥 docker service
                database="video_analytics",
                user="postgres",
                password="",
                port=5432
            )
            print("✅ Connected to DB")
            return conn
        except Exception as e:
            print("DB connection failed, retrying...", e)
            time.sleep(2)

conn = connect_db()
cur = conn.cursor()

buffer = []

# -----------------------------
# MQTT MESSAGE HANDLER
# -----------------------------
def on_message(client, userdata, msg):
    global buffer

    try:
        data = json.loads(msg.payload)
        buffer.append(data)

        if len(buffer) >= 50:
            insert_batch()

    except Exception as e:
        print("MQTT parse error:", e)

# -----------------------------
# BATCH INSERT
# -----------------------------
def insert_batch():
    global buffer

    try:
        for d in buffer:
            cur.execute("""
                INSERT INTO video_events 
                (time, camera_id, object_type, confidence, bbox, track_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datetime.utcnow(),
                d.get("camera_id"),
                d.get("object_type"),
                d.get("confidence"),
                json.dumps(d.get("bbox")),
                d.get("track_id")
            ))

        conn.commit()
        print(f"✅ Inserted {len(buffer)} events")
        buffer.clear()

    except Exception as e:
        print("❌ DB ERROR:", e)
        conn.rollback()

# -----------------------------
# MQTT CLIENT
# -----------------------------
client = mqtt.Client()
MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

while True:
    try:
        print(f"Connecting to MQTT at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        print("✅ Connected to MQTT")
        break
    except Exception as e:
        print("❌ MQTT connection failed, retrying...", e)
        time.sleep(2)
client.subscribe("video/events")
client.on_message = on_message

print("🚀 Listening to MQTT...")
client.loop_forever()