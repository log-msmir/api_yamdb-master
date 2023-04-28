FROM python:3.8-alpine
RUN mkdir /code
COPY requirements.txt /code
RUN apk add --no-cache gcc musl-dev python3-dev
RUN  apk add --update py-pip && pip install -r /code/requirements.txt
COPY . /code
WORKDIR /code
RUN ["chmod", "+x", "./docker-entrypoint.sh"]
ENTRYPOINT ["./docker-entrypoint.sh"]