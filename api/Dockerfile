FROM python:3.6-alpine

COPY . /threatplaybook

WORKDIR /threatplaybook

RUN apk update && apk add python3-dev libffi-dev openssl-dev build-base

RUN pip3 install --upgrade pip && pip3 install pipenv setuptools cffi

RUN pip install -r requirements.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
CMD ["CMD /wait", "/usr/local/bin/python3.6 /threatplaybook/app.py"]
