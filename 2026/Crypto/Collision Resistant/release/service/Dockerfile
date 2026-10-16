FROM python:3.13-alpine

RUN apk add --no-cache socat && adduser -D -H ctf

COPY main.py /run.py
COPY run.sh /run.sh
RUN chmod 555 /run.py /run.sh

USER ctf
EXPOSE 5000

CMD ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:/run.sh,stderr"]
