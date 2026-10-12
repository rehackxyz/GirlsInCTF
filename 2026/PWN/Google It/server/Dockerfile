FROM debian:bookworm-slim

ARG CHROME_URL=https://storage.googleapis.com/chrome-for-testing-public/150.0.7871.46/linux64/chrome-linux64.zip
ARG CHROME_SHA256=ad115a7498a17f53f6ed0914458326c6516addc756224db14c32184a9b1ab078
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl fonts-liberation libasound2 libatk-bridge2.0-0 \
      libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libcurl4 libdbus-1-3 \
      libexpat1 libgbm1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 \
      libpango-1.0-0 libudev1 libvulkan1 libx11-6 libxcb1 libxcomposite1 \
      libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 python3 \
      unzip xdg-utils \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "$CHROME_URL" -o /tmp/chrome-linux64.zip \
 && echo "$CHROME_SHA256  /tmp/chrome-linux64.zip" | sha256sum -c - \
 && unzip -q /tmp/chrome-linux64.zip -d /opt \
 && rm /tmp/chrome-linux64.zip \
 && useradd --uid 1000 --user-group --no-create-home \
      --home-dir /tmp/v8ctf-home chrome

WORKDIR /app
COPY src/server.py /app/server.py
COPY src/gate.py /app/gate.py
RUN chmod 0555 /app/server.py /app/gate.py

USER 1000:1000
EXPOSE 1337
ENTRYPOINT ["python3", "/app/server.py"]
