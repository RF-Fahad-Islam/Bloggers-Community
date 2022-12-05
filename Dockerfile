FROM python:3-alpine3.11

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]