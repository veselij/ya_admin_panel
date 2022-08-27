FROM python:3.10

ENV HOME=/code_test

RUN apt-get update -y && apt-get upgrade -y && apt-get install netcat -y && apt-get install postgresql-client -y
RUN addgroup web && adduser web --home $HOME --ingroup web

WORKDIR $HOME

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./tests .
COPY ./tests/entrypoint.sh /usr/local/bin

USER web

ENTRYPOINT ["entrypoint.sh"]
