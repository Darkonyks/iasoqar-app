FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instaliraj zavisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
