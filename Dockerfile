FROM python:3.8-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 1

RUN apk update \
    && apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo libxml2-dev libxslt-dev \
    && pip install --upgrade pip \
    && pip install cryptography --no-binary cryptography

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN adduser -D metalarchives
USER metalarchives

# run gunicorn
CMD scrapy crawl metal-archives