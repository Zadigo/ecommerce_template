FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

LABEL "com.ecommerce.vendor"="ecommerce"

COPY ./start.sh /start/
RUN chmod +x ./start/start.sh

RUN mkdir /app

WORKDIR /app

RUN pip install --upgrade pip

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip3 install pipenv
RUN pipenv install --deploy --system

COPY . /app/

EXPOSE 8000

# Start project using a simple script file
# ENTRYPOINT [ "../start/start.sh" ]
# ...or with development server
# ENTRYPOINT [ "python", "/app/manage.py", "runserver", "0.0.0.0:8000" ]
# CMD pipenv run python manage.py runserver 0.0.0.0:8000
# ...or Gunicorn for production purposes
# CMD gunicorn nawoka.wsgi -w 4 -b 0.0.0.0:8000 --chdir=/code/nawoka --log-file -
CMD gunicorn ecommerce.wsgi -w 4 -b 0.0.0.0:8000 --chdir=/app/ecommerce --log-level=debug --log-file=/var/gunicorn_log.log
