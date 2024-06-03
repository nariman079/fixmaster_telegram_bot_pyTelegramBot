FROM python:3.11
ENV PYTHONUNBUFFERED=1
RUN pip install -r req.txt
WORKDIR /bot/
COPY . /bot/
