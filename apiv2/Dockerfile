FROM python:3.7

WORKDIR /apps/

COPY ./ /apps/

WORKDIR /apps/tp_api

RUN pip install -U pip setuptools && pip install -r /apps/requirements.txt

EXPOSE 5000

ENTRYPOINT ["python"]

CMD ["app.py"]