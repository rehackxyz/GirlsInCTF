FROM python:3.11-slim

WORKDIR /app

# copy files
COPY app.py requirements.txt flag.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9090

# run as non-root user for safety
RUN useradd -m -u 1000 ctfuser
USER ctfuser

CMD ["python", "app.py"]
