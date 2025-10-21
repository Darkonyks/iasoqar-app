FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instaliraj sistemske zavisnosti potrebne za kompilaciju Python paketa
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    python3-dev \
    libffi-dev \
    libpq-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf-2.0-dev \
    libgirepository1.0-dev \
    gir1.2-pango-1.0 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instaliraj Python zavisnosti
COPY requirements.txt .
# Upgrade pip i instaliraj wheel pre ostalih paketa
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Kopiraj projekat
COPY . .

# Kreiraj potrebne direktorijume
RUN mkdir -p /app/static /app/media

# Prikupi statičke fajlove
RUN python manage.py collectstatic --noinput

# Izloži port
EXPOSE 8000

# Dodavanje entrypoint skripte
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint i komanda za pokretanje
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
