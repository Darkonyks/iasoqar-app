# Redosled importovanja podataka

# 0. Učitaj standarde (automatski se učitava ako ne postoji)
python manage.py loaddata standard_definitions

# 1. IAF/EAC kodovi (mora biti prvi)
python manage.py import_iaf_codes documents/kodovi.xlsx

# 2. Kompanije i nadzorne provere (prima oba fajla)
# Automatski učitava standard_definitions fixture ako ne postoji
python manage.py import_company_data company-list.xlsx naredne-provere.xlsx

# 3. Auditori i njihovi kodovi
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx