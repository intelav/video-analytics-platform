FROM python:3.10-slim

WORKDIR /app

RUN pip install pymodbus==2.5.3

COPY server.py .

CMD ["python", "server.py"]