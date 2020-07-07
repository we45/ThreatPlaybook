FROM python:alpine3.7
COPY tp_api/ /app
COPY requirements.txt /app
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait ./wait
RUN chmod +x ./wait
WORKDIR /app
RUN chmod +x wait-for
RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev libressl-dev && \
    apk add --no-cache --update python3 && \
    pip3 install --upgrade pip setuptools
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["/usr/local/bin/python", "/app/app.py"]