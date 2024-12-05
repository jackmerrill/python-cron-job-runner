FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y python3-full && rm -rf /var/lib/apt/lists/*
COPY ./localbin /localbin

RUN python3 -m venv /venv && bash -c 'cd /venv && source bin/activate && python -m pip install -r /localbin/requirements.txt'

ENTRYPOINT ["/localbin/entrypoint.sh"]