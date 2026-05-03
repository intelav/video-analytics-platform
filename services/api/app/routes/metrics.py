from fastapi import APIRouter
import psycopg2

router = APIRouter()

def get_conn():
    return psycopg2.connect(
        dbname="video_analytics",
        user="postgres",
        password="noida1**",
        host="timescaledb",
        port="5432"
    )

# --------------------------------
# Telemetry (system stats)
# --------------------------------
@router.get("/telemetry")
def get_telemetry():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT time, device, protocol, metrics
        FROM telemetry
        ORDER BY time DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "time": str(r[0]),
            "device": r[1],
            "protocol": r[2],
            "metrics": r[3]
        } for r in rows
    ]


# --------------------------------
# Video Events (detections)
# --------------------------------
@router.get("/events")
def get_events():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT time, camera_id, object_type, confidence, bbox
        FROM video_events
        ORDER BY time DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "time": str(r[0]),
            "camera": r[1],
            "object": r[2],
            "confidence": r[3],
            "bbox": r[4]
        } for r in rows
    ]