FROM python:alpine3.7
COPY tp_api/ /app
COPY requirements.txt /app
WORKDIR /app
RUN apk update && apk add --no-cache openssl-dev libffi-dev gcc musl-dev
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["/usr/local/bin/python", "/app/app.py"]