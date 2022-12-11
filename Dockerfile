FROM python:3.10-alpine
WORKDIR /app
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV GOOGLE_CLIENT_ID=535565541200-pjl74hijcitc536qb743qr6ml5ei5h69.apps.googleusercontent.com
ENV GOOGLE_CLIENT_SECRET=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
ENV SQLALCHEMY_DATABASE_URI=postgresql://doadmin:AVNS__7dxu2VHCcjqKBQM7kF@app-74a7bdad-856f-4a27-9175-78bfd5c24bd4-do-user-13022216-0.b.db.ondigitalocean.com:25060/defaultdb?sslmode=require
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn","-w","4","app:app", "-b", "0.0.0.0"]