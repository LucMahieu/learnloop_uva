# Gebruik de officiële Python 3.8 slim image als basis
FROM python:3.8-slim

# Stel de werkdirectory in de Docker-container in
WORKDIR /app
 
# Kopieer de requirements.txt eerst om gebruik te maken van Docker's caching-laag
COPY requirements.txt .

# Installeer de benodigde Python-pakketten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer nu de rest van de applicatiebestanden naar de werkdirectory
COPY . .

# Stel de poort in die door de container zal worden gebruikt
EXPOSE 8501

# Definieer het commando om de Streamlit-applicatie te starten
CMD ["streamlit", "run", "code/app/main.py"]