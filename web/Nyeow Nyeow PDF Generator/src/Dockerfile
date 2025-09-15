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

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5500
CMD ["python3", "app.py"]
