FROM python:3.10-alpine

WORKDIR /api

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.2/wait /wait
RUN chmod +x /wait

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
RUN pip install -e fastapi-distributed-websocket

COPY ./app ./app
COPY ./tests ./tests

#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT [ "python3", "-m", "app.main" ]
# ENTRYPOINT ["sh", "-c", "/wait && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload --proxy-headers"]
