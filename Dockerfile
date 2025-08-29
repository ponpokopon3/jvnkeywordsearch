# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.11-slim

# Pip
RUN pip install --no-cache-dir requests feedparser

WORKDIR /app
COPY ./app/app.py .
COPY ./app/keywords.csv .
