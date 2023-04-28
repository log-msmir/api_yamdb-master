FROM python:3.8-alpine
RUN mkdir /code
COPY requirements.txt /code
RUN apk add --no-cache gcc musl-dev python3-dev
RUN  apk add --update py-pip && pip install -r /code/requirements.txt
COPY . /code
WORKDIR /code
RUN mkdir /certbot && mkdir /certbot/conf && mkdir /certbot/www && mkdir /certbot/conf/live \
    && mkdir /certbot/conf/live/yamdb.ru/
ENTRYPOINT ["./docker-entrypoint.sh"]