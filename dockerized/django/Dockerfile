FROM python:3.8.7-slim

ENV WEB_HOME=/home/app/web
ENV APP_HOME=/home/app

RUN mkdir -p $WEB_HOME
WORKDIR $WEB_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Adding proper user to run the application
RUN addgroup --system app && adduser --system --group app

# Installing dependencies
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc netcat  -y

RUN pip install --upgrade pip

COPY ./source_files $WEB_HOME

RUN pip install -r requirements.txt
RUN pip install -r requirements.prod.txt

# Permissions for app user
RUN chown -R app:app $APP_HOME

USER app