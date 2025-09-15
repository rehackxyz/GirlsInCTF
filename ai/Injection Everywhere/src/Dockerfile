# Use official Python image
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ /app/

EXPOSE 5000
CMD ["python", "flask_app.py"]