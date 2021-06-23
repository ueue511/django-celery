FROM python:3.6-alpine

ENV CELERY_BROKER_URL redis://redis:6379
# ENV CELERY_RESULT_BACKEND redis://redis:6379
ENV C_FORCE_ROOT true

COPY . /queue
WORKDIR /queue

RUN pip install -r requirements.txt

# WORKDIR /queue/app

# ENTRYPOINT celery -A test_any worker --loglevel=info
