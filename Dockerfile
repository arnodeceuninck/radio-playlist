FROM python:3.9

WORKDIR /ap

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
