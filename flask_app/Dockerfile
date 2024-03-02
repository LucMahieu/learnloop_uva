# Base image
FROM python:3.8-slim

WORKDIR /flask_app

# Copy and cache dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of files to work directory
COPY . .

# Set port used by container
EXPOSE 3000

# Define command to start the Flask app
CMD ["python", "surfconext.py"]
