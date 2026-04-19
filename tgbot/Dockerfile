FROM python:3.11-slim

RUN apt-get update && apt-get install -y locales locales-all
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

WORKDIR /src

COPY requirements.txt /src
RUN pip install -r /src/requirements.txt
COPY . /src

