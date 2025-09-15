FROM python:3.11-slim

# Install TeX (minimal set sufficient for this challenge)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7002
ENV FLASK_ENV=production
CMD ["python", "app.py"]
