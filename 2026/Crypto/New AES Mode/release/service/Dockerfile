FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends socat && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pycryptodome==3.23.0
RUN useradd --system --no-create-home ctf

COPY main.py /run.py
COPY run.sh /run.sh
RUN chmod 555 /run.py /run.sh

USER ctf
EXPOSE 5000
CMD ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:/run.sh,stderr"]
