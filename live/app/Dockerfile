FROM python:3.9

WORKDIR /app
COPY requirements.txt /app

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app
COPY ./source/models /models
COPY ./source/data /data

ENV PYTHONPATH "${PYTHONPATH}:/app"