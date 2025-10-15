FROM python:3.13-slim

MAINTAINER "Lorenz Ritsch"

WORKDIR /app

RUN useradd -m appuser

USER appuser


COPY requirements.txt /tmp/requirements.txt

COPY ./app /app


RUN apt update 
RUN pip install -r /tmpt/requirements.txt

CMD ["./start_api.sh"]