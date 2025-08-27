FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt /app/requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY frontend/ /app

# Exponer puerto
EXPOSE 8501

# deffault command
CMD ["streamlit","run","frontend/app.py","--server.port=8501","--server.address=0.0.0.0"]