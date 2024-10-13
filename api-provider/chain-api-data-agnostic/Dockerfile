FROM python:3.8-slim

WORKDIR /app

COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
