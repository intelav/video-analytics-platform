FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install psycopg2-binary paho-mqtt pika

CMD ["python", "mqtt_to_timescale.py"]