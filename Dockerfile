FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations

COPY scripts ./scripts
RUN chmod +x scripts/start.sh
ENTRYPOINT ["scripts/start.sh"]
