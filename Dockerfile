FROM python:3.10-alpine
WORKDIR /app
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV GOOGLE_CLIENT_ID=535565541200-pjl74hijcitc536qb743qr6ml5ei5h69.apps.googleusercontent.com
ENV GOOGLE_CLIENT_SECRET=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
ENV SQLALCHEMY_DATABASE_URI=postgresql://root:root@167.71.225.190:5432/mydb
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn","-w","4","app:app", "-b", "0.0.0.0"]