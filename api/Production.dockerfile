FROM python:3.10-alpine

WORKDIR /api

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    git \
    gcc \
    libc-dev \
    geos-dev \
    && python3 -m pip install --upgrade pip \
    && CASS_DRIVER_BUILD_CONCURRENCY=8 pip install -r requirements.txt

RUN git clone https://github.com/Leander-van-Boven/fastapi-distributed-websocket.git
RUN pip install ./fastapi-distributed-websocket

COPY ./app ./app

CMD ["python3", "-m", "app.main"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
