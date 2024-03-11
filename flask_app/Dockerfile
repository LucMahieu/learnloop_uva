# Base image
# FROM tiangolo/uwsgi-nginx-flask:python3.8
FROM python:3.8-slim

WORKDIR /app

# Copy and cache dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of files to work directory
COPY . .

# # Copy modified nginx configuration
# COPY server.conf /etc/nginx/conf.d/server.conf

CMD ["python", "main.py"]

# Set port used by container
EXPOSE 3000
