# Import IAF/EAC kodova iz Excel fajla

## Preduslovi

- Docker dev okruženje je pokrenuto (`docker-compose.dev.yml`)
- Excel fajl `kodovi.xlsx` se nalazi u `documents/` folderu
- Excel mora imati kolone: `IAF Scope Reference`, `IAF/EAC Code`, `Code Description`

## Komande za import

### 1. Uđi u Docker container

```bash
docker compose -f docker-compose.dev.yml exec web bash
```

### 2. Probni prikaz (dry-run)

Prikazuje šta bi se importovalo **bez upisa u bazu**:

```bash
python manage.py import_iaf_codes documents/kodovi.xlsx --dry-run
```

### 3. Pravi import sa brisanjem postojećih podataka

**Briše sve postojeće** IAF Scope References i IAF/EAC kodove, zatim uvozi nove iz Excela:

```bash
python manage.py import_iaf_codes documents/kodovi.xlsx --clear-existing
```

### 4. Import bez brisanja postojećih podataka

Dodaje nove kodove **bez brisanja** postojećih:

```bash
python manage.py import_iaf_codes documents/kodovi.xlsx
```

## Šta komanda radi

1. Čita Excel fajl (`documents/kodovi.xlsx`)
2. Grupiše redove po `IAF Scope Reference` (npr. "IAF 1 Agriculture, forestry and fishing")
3. Kreira `IAFScopeReference` zapise (ekstraktuje broj i opis)
4. Za svaki kod iz kolone `IAF/EAC Code` kreira `IAFEACCode` zapis
5. Povezuje svaki kod sa odgovarajućim scope reference-om

## Struktura Excel fajla

| IAF Scope Reference | IAF/EAC Code | Code Description |
|---------------------|--------------|------------------|
| IAF 1 Agriculture, forestry and fishing | 01a | Growing of crops |
|  | 01b | Animal production |
|  | 01c | Mixed farming |

- Prva kolona može biti merged (scope se ponavlja za sve kodove ispod)
- Komanda automatski grupiše kodove koji pripadaju istom scope-u

## Napomene

- Komanda koristi `pandas` za čitanje Excel fajla
- Očekuje sheet naziva `Sheet1` (može se promeniti u kodu ako je potrebno)
- Ako kod već postoji u bazi, neće ga duplicirati (koristi `get_or_create`)
