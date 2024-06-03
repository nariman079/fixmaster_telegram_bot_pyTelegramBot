FROM python:3.11
ENV PYTHONUNBUFFERED=1
COPY req.txt .
RUN pip install -r req.txt
WORKDIR /bot/
COPY . /bot/
