FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY server /app/server
RUN mkdir -p /data && chown -R 10001:10001 /data
USER 10001:10001
CMD ["python", "-m", "server.controller"]
