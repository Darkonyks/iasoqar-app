#!/bin/bash

# Sačekaj da baza bude dostupna
echo "Čekanje da PostgreSQL bude dostupan..."
sleep 5

# Pokreni migracije
echo "Primenjujem migracije..."
python manage.py migrate

# Prikupi statičke fajlove pri svakom pokretanju
echo "Prikupljam statičke fajlove..."
python manage.py collectstatic --noinput

# Nastavi sa izvršavanjem CMD komande
exec "$@"
