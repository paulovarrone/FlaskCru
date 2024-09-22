FROM python:3


WORKDIR /usr/src/app


COPY requirements.txt ./


RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

EXPOSE 5000


CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000" ]
