FROM python:3.10-slim

WORKDIR /app

RUN pip install opcua

COPY server.py .

CMD ["python", "server.py"]