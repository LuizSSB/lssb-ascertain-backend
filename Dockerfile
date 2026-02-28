FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# use /app as the working directory so relative paths are predictable
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source tree into image – in dev we will mount over this
COPY . .

COPY scripts ./scripts
RUN chmod +x scripts/start.sh
ENTRYPOINT ["scripts/start.sh"]
