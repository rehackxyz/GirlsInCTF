FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and wkhtmltopdf dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    wkhtmltopdf \
    libxrender1 libxext6 libfontconfig \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python3","app.py"]