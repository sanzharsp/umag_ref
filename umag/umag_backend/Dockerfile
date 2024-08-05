FROM python:3.10.9

RUN apt-get update -y
RUN apt-get --fix-missing install
RUN apt-get upgrade -y

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src ./src

#CMD gunicorn -w 4 --chdir ./src kazalem.wsgi --bind 0.0.0.0:8000
CMD gunicorn -w 4 --chdir ./src umag_backend.wsgi --bind 0.0.0.0:8004
