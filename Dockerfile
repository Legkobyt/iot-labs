FROM python:3.13-slim

RUN pip install apprise loguru paho-mqtt pydantic pydantic-settings

COPY src/ /app

WORKDIR /app
CMD ["python", "main.py"]
