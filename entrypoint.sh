#!/bin/bash

# Funkcija za čekanje baze
wait_for_db() {
    echo "Čekanje da PostgreSQL bude dostupan..."
    
    # Čekaj dok baza ne bude dostupna
    until python -c "
import os
import psycopg
try:
    conn = psycopg.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        dbname=os.environ.get('POSTGRES_DB', 'isoqar')
    )
    conn.close()
    print('Baza je dostupna!')
except Exception as e:
    print(f'Baza još nije dostupna: {e}')
    exit(1)
"; do
        echo "Čekam bazu..."
        sleep 2
    done
}

# Čekaj bazu samo ako koristimo PostgreSQL
if [ "$DATABASE_URL" = "postgresql" ] || [ "$DATABASE_URL" = "postgres" ]; then
    wait_for_db
fi

# Pokreni migracije
echo "Primenjujem migracije..."
python manage.py migrate

# Prikupi statičke fajlove
echo "Prikupljam statičke fajlove..."
python manage.py collectstatic --noinput

# Nastavi sa izvršavanjem CMD komande
exec "$@"
