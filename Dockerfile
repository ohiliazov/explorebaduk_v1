FROM python:3.8-buster

EXPOSE 8080

WORKDIR /opt/explorebaduk

ADD ./requirements.txt /opt/explorebaduk/requirements.txt
ADD ./Makefile /opt/explorebaduk/Makefile

RUN make install

ADD . /opt/explorebaduk

CMD make serve
