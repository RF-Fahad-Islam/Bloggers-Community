FROM python:3-alpine

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "app:app"]