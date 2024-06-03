FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /bot/
COPY req.txt /bot/
RUN pip install -r req.txt
COPY . /bot/
