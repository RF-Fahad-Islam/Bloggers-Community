FROM python:3.10-alpine
WORKDIR /app
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV GOOGLE_CLIENT_ID=your-secret
ENV GOOGLE_CLIENT_SECRET=your-secret
ENV SQLALCHEMY_DATABASE_URI=postgresql://root:root@ip:port/mydb
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn","-w","4","app:app", "-b", "0.0.0.0"]
