FROM ubuntu:20.04

RUN apt update && apt install -y python3.8 pip python-is-python3

WORKDIR /task

ADD requirements.txt .
RUN pip install -r requirements.txt && pip -V

ADD . .

RUN python -V

