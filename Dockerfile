FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
RUN mkdir /digipay
WORKDIR /digipay
COPY . /digipay

# Installing requirements
RUN apt-get update && apt-get install -y gcc
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
