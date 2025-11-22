# 📊 Import Podataka iz Excel Fajlova

## Pregled

Ovaj dokument opisuje kako importovati podatke kompanija i nadzornih provera iz Excel fajlova u ISOQAR aplikaciju.

---

## 📋 Potrebni Fajlovi

### 1. **company-list.xlsx** - Lista kompanija

**Kolone:**
| Kolona | Opis | Tip | Obavezno |
|--------|------|-----|----------|
| `company_id` | Jedinstveni ID kompanije | Integer | ✅ |
| `company_name` | Naziv kompanije | Text | ✅ |
| `certificate_number` | Broj sertifikata | Text | ❌ |
| `IAF_kod_id` | ID IAF/EAC koda | Integer/Text | ❌ |
| `standard_id` | ID standarda | Integer/Text | ❌ |
| `certificate_start` | Datum početka sertifikata | Date | ❌ |
| `suspension_until_date` | Suspenzija do datuma | Date | ❌ |
| `audit_days` | Broj dana audita | Decimal | ❌ |
| `visits_per_year` | Poseta godišnje | Integer | ❌ |
| `audit_days_each` | Dana po auditu | Decimal | ❌ |
| `contracted_date` | Datum ugovora | Date | ❌ |

**Primer:**
```
company_id | company_name | certificate_number | IAF_kod_id | standard_id | certificate_start | ...
1          | INOAQLEX     | 6211              | 28         | 1           | 19-11-2016       | ...
2          | INOAQTEX     | 6301              | 17         | 1           | 26-02-2015       | ...
```

### 2. **naredne-provere.xlsx** - Nadzorne provere

**Kolone:**
| Kolona | Opis | Tip | Obavezno |
|--------|------|-----|----------|
| `naredne_provere_id` | ID provere | Integer | ✅ |
| `company_id` | ID kompanije (mora postojati u company-list) | Integer | ✅ |
| `first_surv_due` | Planirani datum prve nadzorne | Date | ❌ |
| `first_surv_cond` | Stvarni datum prve nadzorne | Date | ❌ |
| `second_surv_due` | Planirani datum druge nadzorne | Date | ❌ |
| `second_surv_cond` | Stvarni datum druge nadzorne | Date | ❌ |
| `trinial_audit_due` | Planirani datum resertifikacije | Date | ❌ |
| `trinial_audit_cond` | Stvarni datum resertifikacije | Date | ❌ |
| `status_id` | Status ID | Integer | ❌ |

**Primer:**
```
naredne_provere_id | company_id | first_surv_due | first_surv_cond | second_surv_due | ...
1                  | 1          | 19-02-2017     | 01-08-2017      | 19-02-2018      | ...
2                  | 2          | 20-10-2016     | 19-04-2017      | 20-10-2017      | ...
```

---

## 🚀 Korišćenje

### 1. Priprema Fajlova

Postavi Excel fajlove u root folder projekta:
```
isoqar-app/
├── company-list.xlsx
├── naredne-provere.xlsx
└── ...
```

### 2. Testiranje Importa (Dry Run)

Pre nego što importuješ podatke u bazu, testiraj sa `--dry-run`:

```bash
# Lokalno (sa aktiviranim venv)
python manage.py import_company_data company-list.xlsx naredne-provere.xlsx --dry-run

# U Docker kontejneru
docker-compose -f docker-compose.dev.yml exec web python manage.py import_company_data company-list.xlsx naredne-provere.xlsx --dry-run
```

**Dry run će:**
- ✅ Učitati podatke iz Excel fajlova
- ✅ Validirati podatke
- ✅ Prikazati šta bi bilo kreirano/ažurirano
- ❌ **NEĆE** sačuvati podatke u bazu

### 3. Stvarni Import

Kada si siguran da je sve u redu, pokreni bez `--dry-run`:

```bash
# Lokalno
python manage.py import_company_data company-list.xlsx naredne-provere.xlsx

# U Docker kontejneru
docker-compose -f docker-compose.dev.yml exec web python manage.py import_company_data company-list.xlsx naredne-provere.xlsx
```

---

## 📊 Šta Skript Radi

### Faza 1: Import Kompanija

1. **Učitava company-list.xlsx**
2. **Za svaku kompaniju:**
   - Kreira novu kompaniju ili ažurira postojeću (po `company_name`)
   - Postavlja osnovne podatke (sertifikat, datumi, broj dana audita)
   - Dodaje standarde (ako je `standard_id` naveden)
   - Dodaje IAF/EAC kodove (ako je `IAF_kod_id` naveden)
   - Kreira `CertificationCycle` (ako postoji `certificate_start`)
   - Kreira inicijalni audit (ako postoji `certificate_start` i `audit_days`)

### Faza 2: Import Nadzornih Provera

1. **Učitava naredne-provere.xlsx**
2. **Za svaku proveru:**
   - Pronalazi kompaniju po `company_id`
   - Pronalazi ili kreira aktivan `CertificationCycle`
   - Kreira **prvu nadzornu proveru** (ako postoji `first_surv_due`)
   - Kreira **drugu nadzornu proveru** (ako postoji `second_surv_due`)
   - Kreira **resertifikacioni audit** (ako postoji `trinial_audit_due`)
   - Postavlja status (`planned` ili `completed`) na osnovu toga da li postoji stvarni datum

---

## 📝 Formati Datuma

Skript podržava sledeće formate datuma:
- `DD-MM-YYYY` (npr. `19-02-2017`)
- `DD.MM.YYYY` (npr. `19.02.2017`)
- `YYYY-MM-DD` (npr. `2017-02-19`)
- `DD/MM/YYYY` (npr. `19/02/2017`)

---

## ⚠️ Napomene i Ograničenja

### Standardi i IAF Kodovi

- Skript pokušava da pronađe standarde i IAF kodove po **ID-u** ili **kodu**
- Ako standard/kod nije pronađen, prikazuje upozorenje ali nastavlja sa importom
- **Pre importa**, proveri da li su svi standardi i IAF kodovi već u bazi

### Duplikati

- Kompanije se identifikuju po **nazivu** (`company_name`)
- Ako kompanija sa istim nazivom već postoji, biće **ažurirana**
- Auditi se identifikuju po **certification_cycle + audit_type + planned_date**
- Ako audit već postoji, **neće biti kreiran duplikat**

### Certification Cycles

- Skript kreira **jedan aktivan cycle** po kompaniji
- Ako kompanija već ima aktivan cycle, koristi postojeći
- Ako nema cycle, kreira novi sa datumom iz `first_surv_due` ili trenutnim datumom

---

## 🔍 Provera Rezultata

Nakon importa, proveri:

### 1. Kompanije

```bash
# Broj kompanija
docker-compose -f docker-compose.dev.yml exec web python manage.py shell
>>> from company.models import Company
>>> Company.objects.count()
```

### 2. Certification Cycles

```bash
>>> from company.models import CertificationCycle
>>> CertificationCycle.objects.count()
```

### 3. Auditi

```bash
>>> from company.models import CycleAudit
>>> CycleAudit.objects.count()
>>> CycleAudit.objects.filter(audit_type='surveillance').count()  # Nadzorne
>>> CycleAudit.objects.filter(audit_type='recertification').count()  # Resertifikacije
```

### 4. Standardi i IAF Kodovi

```bash
>>> from company.models import CompanyStandard, CompanyIAFEACCode
>>> CompanyStandard.objects.count()
>>> CompanyIAFEACCode.objects.count()
```

---

## 🐛 Troubleshooting

### Problem: "Kompanija sa ID X nije pronađena"

**Uzrok:** `company_id` u `naredne-provere.xlsx` ne postoji u `company-list.xlsx`

**Rešenje:**
- Proveri da li su ID-evi konzistentni između dva fajla
- Prvo importuj kompanije, pa tek onda provere

### Problem: "Standard X nije pronađen"

**Uzrok:** Standard sa tim ID-em ili kodom ne postoji u bazi

**Rešenje:**
```bash
# Proveri postojeće standarde
docker-compose -f docker-compose.dev.yml exec web python manage.py shell
>>> from company.models import StandardDefinition
>>> StandardDefinition.objects.all().values('id', 'code', 'name')
```

### Problem: "IAF kod X nije pronađen"

**Uzrok:** IAF/EAC kod sa tim ID-em ili kodom ne postoji u bazi

**Rešenje:**
```bash
# Proveri postojeće IAF kodove
>>> from company.models import IAFEACCode
>>> IAFEACCode.objects.all().values('id', 'code', 'description')
```

### Problem: Datum nije parsiran

**Uzrok:** Format datuma nije podržan

**Rešenje:**
- Proveri da li datum u Excel-u ima podržan format
- Ako je potrebno, konvertuj datume u Excel-u u format `DD-MM-YYYY`

---

## 📚 Dodatni Resursi

- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [ISOQAR Models Documentation](./company/models.py)

---

## 💬 Podrška

Za pomoć kontaktiraj DevOps tim ili otvori issue na GitHub-u.
