FROM python:3.12-bookworm

RUN apt-get update && apt-get upgrade -y
RUN apt-get install openssh-client -y

WORKDIR /application

RUN mkdir /application/data
COPY dependencies dependencies
# COPY dependencies/.env /application

# Setup .ssh.
RUN mkdir /root/.ssh
COPY dependencies/.ssh /root/.ssh
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/id_ed25519
RUN ssh-keyscan gitlab.com >> /root/.ssh/known_hosts
RUN chmod 644 /root/.ssh/known_hosts

RUN pip install git+ssh://git@github.com/dantimofte/smarthouse.git
