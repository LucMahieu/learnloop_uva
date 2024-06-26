FROM python:3.12-slim

WORKDIR /student_app

COPY ./learnloop ./learnloop
# Copy the requirements file first
# COPY student_app/requirements.txt .

COPY ./student_app .

RUN pip install --no-cache-dir -r requirements.txt

# Ensure that the logs are printed while running in docker
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "src/main.py"]