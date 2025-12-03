FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Variables de entorno
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Puerto de la aplicación
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:application"]
