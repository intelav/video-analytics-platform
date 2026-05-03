# db/writer.py
import psycopg2
import json

conn = psycopg2.connect(
    dbname="video_analytics",
    user="postgres",
    password="yourpass",
    host="localhost",
    port=5432
)

def insert_telemetry(data):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO telemetry (time, device, protocol, metrics)
        VALUES (NOW(), %s, %s, %s)
    """, (
        data["device_id"],
        data["protocol"],
        json.dumps(data["metrics"])
    ))
    conn.commit()