FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

LABEL "com.mywebsite.version"="1.0"

RUN mkdir /app

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN python -m pip install pipenv
# RUN python -m pip install pipenv==2018.10.13
RUN pipenv install --deploy --system

RUN apt update

RUN apt-get install memcached

COPY . /app/

EXPOSE 8000

# Start project using a simple script file
# ENTRYPOINT [ "../start/start.sh" ]
# ...or with development server
# ENTRYPOINT [ "python", "/app/manage.py", "runserver", "0.0.0.0:8000" ]
# CMD pipenv run python manage.py runserver 0.0.0.0:8000
# ...or Gunicorn for production purposes
# CMD gunicorn mywebsite.wsgi -w 4 -b 0.0.0.0:8000 --chdir=/app/mywebsite --log-file -
# CMD gunicorn mywebsite.wsgi -w 4 -b 0.0.0.0:8000 --chdir=/app/mywebsite --log-level=debug --log-file=/var/gunicorn_log.log
