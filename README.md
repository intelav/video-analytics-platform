
cd /media/avaish/aiwork/video-analytics-platform/infrastructure/docker
docker compose up --build
docker compose up
docker compose down
docker compose logs timescaledb
curl http://localhost:8000/
psql -h localhost -p 5432 -U postgres -d video_analytics
docker exec -it timescaledb psql -U postgres -d video_analytics


Timescale DB
==============
\dx
\c
SELECT * FROM timescaledb_information.chunks;

Creatnig tables
=================
CREATE TABLE telemetry (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT,
    temperature DOUBLE PRECISION,
    cpu_usage DOUBLE PRECISION,
    memory_usage DOUBLE PRECISION,
    location JSONB
);

SELECT create_hypertable('telemetry', 'time');

CREATE TABLE video_events (
    time TIMESTAMPTZ NOT NULL,
    camera_id TEXT,
    object_type TEXT,
    confidence FLOAT,
    bbox JSONB,
    track_id TEXT
);
SELECT create_hypertable('video_events', 'time');

CREATE TABLE cameras (
    id TEXT PRIMARY KEY,
    location TEXT,
    rtsp_url TEXT
);


INSERT INTO telemetry VALUES (
    NOW(),
    'jetson-test',
    55.2,
    70.1,
    60.5,
    '{"lat":12.97,"lon":77.59}'
);

Instllation
==============
sudo apt update
sudo apt install -y gnupg postgresql-common

psql --version
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt update
sudo apt install -y gnupg postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt install timescaledb-2-postgresql-14
sudo timescaledb-tune
sudo systemctl restart postgresql
CREATE DATABASE video_analytics;
\c video_analytics;
CREATE EXTENSION IF NOT EXISTS timescaledb;
pip install psycopg2-binary

Query Tmescale DB
=============
SELECT * FROM telemetry ORDER BY time DESC LIMIT 10;
SELECT * FROM telemetry;
SELECT * FROM timescaledb_information.hypertables;
Aggregation - 
SELECT time_bucket('1 minute', time) AS bucket,
       avg(temperature)
FROM telemetry
GROUP BY bucket
ORDER BY bucket DESC;

SELECT * 
FROM video_events 
ORDER BY time DESC 
LIMIT 10;

Chunk info
=============
SELECT * FROM timescaledb_information.chunks;

Authentication FIx
================
sudo nano /etc/postgresql/14/main/pg_hba.conf
local   all             postgres                                md5

Password change
==============
sudo -u postgres psql
ALTER USER postgres PASSWORD 'yourpassword';
sudo systemctl restart postgresql


Creating Indexes
=============
CREATE INDEX ON telemetry (device_id, time DESC);
CREATE INDEX ON video_events (camera_id, time DESC);

Retention Policy
===============
SELECT add_retention_policy('telemetry', INTERVAL '7 days');
SELECT * FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention';

Compression Policy
================
ALTER TABLE telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id'
);

SELECT add_compression_policy('telemetry', INTERVAL '1 day');
SELECT * FROM chunk_compression_stats('telemetry');
SELECT * FROM timescaledb_information.jobs WHERE proc_name = 'policy_compression';
SELECT compress_chunk('_timescaledb_internal._hyper_2_1_chunk');

JSONB and GIN(Generalized Inverted Index)
=================
ALTER TABLE video_events
ALTER COLUMN bbox TYPE JSONB USING bbox::jsonb;


Counting
=============
SELECT COUNT(*) FROM video_events;
SELECT COUNT(*) 
FROM video_events
WHERE time > NOW() - INTERVAL '10 minute';
SELECT camera_id, COUNT(*) 
FROM video_events
GROUP BY camera_id;

SELECT date_trunc('second', time) AS ts, COUNT(*)
FROM video_events
GROUP BY ts
ORDER BY ts DESC
LIMIT 10;


=============
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
mosquitto_sub -t test
mosquitto_pub -t test -m "hello"

mosquitto_sub -t video/events

RabitMQ
==========
http://localhost:15672/,guest,guest,