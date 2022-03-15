FROM locustio/locust

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /digipay
COPY . /digipay

# Installing requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
