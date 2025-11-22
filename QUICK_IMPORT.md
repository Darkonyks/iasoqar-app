# 🚀 Brzi Vodič za Import Podataka

## 📋 Koraci

### 1. Pripremi Excel Fajlove

Postavi fajlove u root folder:
```
isoqar-app/
├── company-list.xlsx
├── naredne-provere.xlsx
```

### 2. Validacija (Preporučeno)

```bash
# Lokalno
python manage.py validate_import_files company-list.xlsx naredne-provere.xlsx

# Docker
docker-compose -f docker-compose.dev.yml exec web \
  python manage.py validate_import_files company-list.xlsx naredne-provere.xlsx
```

**Šta validacija proverava:**
- ✅ Da li fajlovi postoje
- ✅ Da li su kolone ispravne
- ✅ Da li postoje duplikati company_id
- ✅ Da li svi company_id iz naredne-provere.xlsx postoje u company-list.xlsx
- ✅ Da li standardi postoje u bazi
- ✅ Da li IAF kodovi postoje u bazi
- ✅ Da li su datumi u validnom formatu

### 3. Test Import (Dry Run)

```bash
# Lokalno
python manage.py import_company_data company-list.xlsx naredne-provere.xlsx --dry-run

# Docker
docker-compose -f docker-compose.dev.yml exec web \
  python manage.py import_company_data company-list.xlsx naredne-provere.xlsx --dry-run
```

**Dry run:**
- ✅ Učitava podatke
- ✅ Prikazuje šta bi bilo kreirano
- ❌ **NE** čuva u bazu

### 4. Stvarni Import

```bash
# Lokalno
python manage.py import_company_data company-list.xlsx naredne-provere.xlsx

# Docker
docker-compose -f docker-compose.dev.yml exec web \
  python manage.py import_company_data company-list.xlsx naredne-provere.xlsx
```

---

## 📊 Primer Output-a

### Validacija:
```
🔍 Validacija Excel fajlova...

📊 Validacija: company-list.xlsx
  Kolone: ['company_id', 'company_name', 'certificate_number', ...]
  ✅ Ukupno redova: 150
  ✅ Sve validacije prošle!

📊 Validacija: naredne-provere.xlsx
  Kolone: ['naredne_provere_id', 'company_id', 'first_surv_due', ...]
  ✅ Ukupno redova: 120
  ✅ Sve validacije prošle!

✅ Validacija uspešna! Fajlovi su spremni za import.
```

### Import:
```
📊 Učitavanje kompanija iz: company-list.xlsx
Kolone: ['company_id', 'company_name', ...]
  Obrađeno 10 redova...
  Obrađeno 20 redova...
  ...
✅ Kompanije: 145 kreirano, 5 ažurirano, 0 preskočeno

📊 Učitavanje nadzornih provera iz: naredne-provere.xlsx
Kolone: ['naredne_provere_id', 'company_id', ...]
  Obrađeno 10 redova...
  Obrađeno 20 redova...
  ...
✅ Nadzorne provere: 118 kreirano, 2 preskočeno
```

---

## ⚠️ Česte Greške

### "Standard X nije pronađen"

**Rešenje:** Prvo dodaj standarde u bazu:
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py shell
>>> from company.models import StandardDefinition
>>> StandardDefinition.objects.create(code='ISO 9001', name='Quality Management')
```

### "IAF kod X nije pronađen"

**Rešenje:** Prvo dodaj IAF kodove u bazu:
```bash
>>> from company.models import IAFEACCode
>>> IAFEACCode.objects.create(code='28', description='Construction')
```

### "Kompanija sa ID X nije pronađena"

**Rešenje:** Proveri da li company_id u naredne-provere.xlsx odgovara company_id u company-list.xlsx

---

## 🔍 Provera Nakon Importa

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py shell

# Broj kompanija
>>> from company.models import *
>>> Company.objects.count()
150

# Broj ciklusa
>>> CertificationCycle.objects.count()
145

# Broj audita
>>> CycleAudit.objects.count()
420

# Nadzorne provere
>>> CycleAudit.objects.filter(audit_type='surveillance').count()
290

# Resertifikacije
>>> CycleAudit.objects.filter(audit_type='recertification').count()
120
```

---

## 📚 Detaljnija Dokumentacija

Za više detalja pogledaj: [IMPORT_GUIDE.md](./IMPORT_GUIDE.md)
