# Import dodela auditora (kategorije, TA, standardi, EAC kodovi)

## Preduslovi

- Docker dev okruženje je pokrenuto (`docker-compose.dev.yml`)
- Excel fajl `Auditori_Tehnicki_eksperti_KODOVI.xlsx` se nalazi u `documents/` folderu
- Excel mora imati kolone: `Auditor`, `Kategorija`, `TA`, `STANDARD`, `EAC`
- **IAF/EAC kodovi moraju biti već importovani u bazu** (koristiti `import_iaf_codes` komandu prvo)

## Redosled importa

### 1. Prvo importuj IAF/EAC kodove

```bash
docker compose -f docker-compose.dev.yml exec web bash
python manage.py import_iaf_codes documents/kodovi.xlsx --clear-existing
```

### 2. Zatim importuj dodele auditora

```bash
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx
```

## Komande za import

### 1. Uđi u Docker container

```bash
docker compose -f docker-compose.dev.yml exec web bash
```

### 2. Probni prikaz (dry-run)

Prikazuje šta bi se importovalo **bez upisa u bazu**:

```bash
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx --dry-run
```

### 3. Pravi import sa brisanjem postojećih dodela

**Briše sve postojeće** veze auditora sa standardima i EAC kodovima, zatim uvozi nove iz Excela:

```bash
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx --clear-existing
```

### 4. Import bez brisanja postojećih dodela

Dodaje nove dodele **bez brisanja** postojećih:

```bash
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx
```

## Šta komanda radi

1. **Učitava jedinstvene auditore** iz Excel fajla
2. **Kreira ili pronalazi auditore** u bazi podataka
3. **Dodeljuje kategoriju** svakom auditoru:
   - Lead auditor
   - Auditor
   - Technical Expert
   - Trainer
4. **Dodeljuje TA (Technical Area) kod** auditoru
5. **Automatski kreira standarde** koji ne postoje u bazi:
   - Mapira kodove iz Excela (npr. "9001") na pune nazive ("ISO 9001:2015")
   - Kreira standard sa osnovnim podacima ako ne postoji
6. **Dodeljuje standarde** auditoru:
   - Ako je `STANDARD = "SVI"` → dodeljuje sve aktivne standarde
   - Inače dodeljuje specifične standarde po kodu
7. **Dodeljuje EAC kodove**:
   - Za **Technical Expert**: EAC kodovi se dodeljuju **direktno auditoru**
   - Za ostale kategorije: EAC kodovi se dodeljuju **standardu auditora**

## Struktura Excel fajla

| Auditor | Kategorija | TA | STANDARD | EAC | COMMENT |
|---------|------------|-----|----------|-----|---------|
| Urosevic Aleksandra | Technical Expert | T09 | SVI | 28a | |
| Urosevic Aleksandra | Technical Expert | T09 | SVI | 28b | |
| Urosevic Aleksandra | Technical Expert | T09 | SVI | 28c | |

### Podržane vrednosti za kolonu "Kategorija":

Skripta automatski mapira različite varijante naziva kategorija:

| Vrednost u Excelu | Mapira se na |
|-------------------|--------------|
| Lead Auditor, Lead auditor, lead_auditor | Lead auditor |
| Auditor, auditor | Auditor |
| Technical Expert, technical_expert, Tehnički ekspert | Tehnički ekspert |
| Trainer, trainer, Trainee | Trainer |

### Napomene o strukturi:

- **Auditor**: Ime i prezime auditora (jedinstveno)
- **Kategorija**: Lead auditor, Auditor, Technical Expert, ili Trainer
- **TA**: Technical Area kod (npr. T09, T11, T12)
- **STANDARD**: 
  - `SVI` ili `ALL` = dodeljuje sve aktivne standarde
  - Specifični kod standarda (npr. `ISO9001`)
- **EAC**: IAF/EAC kod (npr. 28a, 28b, 19g)
- **COMMENT**: Opciono polje za napomene (trenutno se ne koristi)

## Logika importa

### Za Technical Expert auditore:

1. Kreira/pronalazi auditora
2. Postavlja kategoriju na "Technical Expert"
3. Dodeljuje TA kod
4. Dodeljuje EAC kodove **direktno auditoru** (ne preko standarda)
5. **NAPOMENA**: Technical Expert auditore **NE DOBIJAJU standarde** - samo direktne EAC kodove

### Za ostale kategorije (Lead auditor, Auditor, Trainer):

1. Kreira/pronalazi auditora
2. Postavlja odgovarajuću kategoriju
3. Dodeljuje TA kod
4. Dodeljuje standarde auditoru:
   - Ako je `STANDARD = "SVI"` → dodeljuje sve aktivne standarde
   - Inače dodeljuje specifične standarde po kodu
5. Dodeljuje EAC kodove **standardu auditora** (ne direktno auditoru)

## Primer korišćenja

```bash
# Uđi u container
docker compose -f docker-compose.dev.yml exec web bash

# Prvo importuj IAF/EAC kodove (ako već nisu)
python manage.py import_iaf_codes documents/kodovi.xlsx --clear-existing

# Zatim importuj dodele auditora (probni prikaz)
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx --dry-run

# Ako je sve ok, pokreni pravi import
python manage.py import_auditor_assignments documents/Auditori_Tehnicki_eksperti_KODOVI.xlsx
```

## Napomene

- Komanda koristi `pandas` za čitanje Excel fajla
- Ako auditor već postoji, ažurira se njegova kategorija i TA kod
- **EAC kodovi se automatski normalizuju** - dodaje se vodeća nula jednocifenim kodovima (npr. "6a" → "06a", "7b" → "07b")
- Ako EAC kod ne postoji u bazi ni nakon normalizacije, ispisuje se upozorenje ali import nastavlja
- **Standardi se automatski kreiraju** ako ne postoje u bazi (vidi tabelu mapiranja ispod)
- Email i telefon auditora se postavljaju na placeholder vrednosti ako se kreira novi auditor
- Komanda koristi `get_or_create` da izbegne duplikate
- **Technical Expert** auditore dobijaju samo direktne EAC kodove, **bez standarda**

## Podržani standardi (automatsko kreiranje)

Komanda automatski kreira standarde koji ne postoje u bazi. Mapiranje kodova:

| Kod u Excelu | Pun naziv standarda |
|--------------|---------------------|
| 9001 | ISO 9001:2015 |
| 14001 | ISO 14001:2015 |
| 45001 | ISO 45001:2018 |
| 27001 | ISO 27001:2022 |
| 22000 | ISO 22000:2018 |
| 50001 | ISO 50001:2018 |
| 20000 | ISO 20000-1:2018 |
| 37001 | ISO 37001:2016 |
| HACCP | HACCP |

**Napomena**: Ako kod nije u mapiranju, kreira se kao `ISO {kod}` (npr. "1090" → "ISO 1090")

## Normalizacija EAC kodova

Komanda automatski normalizuje EAC kodove dodavanjem vodeće nule jednocifenim kodovima:

| Kod u Excelu | Normalizovan kod | Status |
|--------------|------------------|--------|
| 6a | 06a | ✅ Automatski normalizovan |
| 7b | 07b | ✅ Automatski normalizovan |
| 9a | 09a | ✅ Automatski normalizovan |
| 28a | 28a | ✅ Već ispravan format |
| 34c | 34c | ✅ Već ispravan format |

**Primer output-a:**
```
✓ EAC kod: 6a -> 06a
✓ EAC kod: 28a -> 28a
✗ EAC kod "5x" (normalizovan: "05x") ne postoji u bazi
```

## Troubleshooting

### Greška: "EAC kod ne postoji u bazi"

**Rešenje**: Prvo importuj IAF/EAC kodove:
```bash
python manage.py import_iaf_codes documents/kodovi.xlsx --clear-existing
```

### Greška: "Standard ne postoji u bazi"

**Rešenje**: ~~Proveri da li standard postoji u `StandardDefinition` modelu ili dodaj novi standard kroz Django admin.~~

**AŽURIRANO**: Ova greška više ne bi trebalo da se dešava - komanda automatski kreira standarde koji ne postoje!

### Greška: "Tehnički ekspert ne može imati dodeljene standarde"

**Rešenje**: Ova greška je **rešena**. Komanda sada pravilno tretira Technical Expert auditore - dodeljuje im samo direktne EAC kodove bez standarda.
