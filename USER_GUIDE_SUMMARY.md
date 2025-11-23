# IASOQAR - Brza Referenca Korisničkog Vodiča

## Glavne Funkcionalnosti Aplikacije

### 1. DASHBOARD
- **URL:** `/dashboard/`
- **Što vidite:** Sveobuhvatni pregled celog sistema sa 4 glavne kartice
- **Kartice:**
  - Pregled - Brze metrike
  - Kompanije - Statistika po statusu
  - Auditi - Pregled audita
  - Srbija Tim - Crni kalendar statistika

### 2. KOMPANIJE
- **URL:** `/companies/`
- **Funkcije:**
  - Kreiranje novih kompanija
  - Pregled detalja
  - Upravljanje standardima
  - Dodela IAF/EAC kodova
  - Upravljanje kontakt osoba
  - Dodavanje lokacija
- **Obavezna Polja Pri Kreiranju:**
  - Naziv
  - Matični broj
  - Industrija
  - Status sertifikata

### 3. AUDITORI
- **URL:** `/auditors/`
- **Kategorije:**
  - Lead Auditor (vodeći auditor)
  - Auditor (redovni auditor)
  - Technical Expert (tehnički ekspert)
  - Trainer (instruktor)
- **Upravljanje:**
  - Dodela standarda
  - Dodela IAF/EAC kodova
  - Praćenje dostupnosti

### 4. SERTIFIKACIJSKI CIKLUSI
- **URL:** `/cycles/`
- **Tipovi Ciklusa:**
  - Initial (inicijalni audit)
  - Surveillance (godišnja nadzorna provera)
  - Recertification (revalidacija)
- **Faze:** Kreiranje → Planiranje → Zakazivanje → Izvršavanje

### 5. KALENDAR
- **URL:** `/calendar/`
- **Mogućnosti:**
  - Pregled svih zakazanih audita
  - Drag-and-drop premještanje
  - Dodavanje novih audita
  - Filtriranje po auditorima
  - Prikazi: Mesečni, Nedeljni, Dnevni

### 6. IAF/EAC KODOVI
- **URL:** `/iaf-codes/`
- **Funkcija:** Specifikacija domene primene standarda
- **Upotreba:**
  - Kompanije imaju kodove (obično jedan primarni)
  - Auditori moraju biti kvalifikovani za kod
  - Sistem filtrira dostupne auditory po kodu

### 7. SRBIJA TIM - CRNI KALENDAR
- **URL:** `/srbija-tim/`
- **Komponente:**
  - Kalendar poseta
  - Lista poseta
  - Raspored auditora
- **Funkcija:** Upravljanje lokalnim timom i posjetama

### 8. LOKACIJE
- **URL:** `/locations/`
- **Funkcija:** Upravljanje dodatnim lokacijama kompanija

### 9. KONTAKT OSOBE
- **Upravljanje:** Kroz stranicu kompanije
- **Funkcija:** Čuvanje kontakt podataka
- **Atributi:** Ime, pozicija, email, telefon, primarna osoba

---

## Brze Akcije

### Kreiraj Novu Kompaniju
1. Kompanije → + Nova Kompanija
2. Popuni obavezna polja
3. Dodaj standarde, kodove, kontakte, lokacije
4. Sačuvaj

### Kreiraj Novu Ciklus
1. Ciklusi → + Novi Ciklus
2. Odaberi kompaniju i tip
3. Definiši standarde
4. Dodaj audite
5. Zakaži u kalendaru

### Dodaj Auditora
1. Auditori → + Novi Auditor
2. Unesi: Ime, Email, Kategorija
3. Dodaj standarde koje može auditirati
4. Dodaj IAF/EAC kodove
5. Sačuvaj

### Zakaži Audit
1. Kalendar → Kliknite na dan
2. Odaberi ciklus
3. Odaberi vodeći auditor
4. Dodaj dodatne auditory
5. Sačuvaj

---

## Struktura Podataka

### Kompanija Sadrži:
```
Kompanija
├── Osnovni Podaci (PIB, MB, Adresa, itd.)
├── Standardi (ISO 9001, ISO 14001, itd.)
├── IAF/EAC Kodovi (A01, B02, itd.)
├── Kontakt Osobe (Direktor, Manager, itd.)
├── Lokacije (Glavna, Fabrike, Skladišta, itd.)
├── Sertifikacijski Ciklusi
│   └── Auditi (Initial, Surveillance, Recer.)
├── Sastanci/Događaji
└── Izveštaji
```

### Auditor Sadrži:
```
Auditor (Kategorija: Lead, Auditor, Expert, Trainer)
├── Osnovni Podaci (Ime, Email, Telefon)
├── Standardi (ISO 9001, ISO 14001, itd.)
│   └── IAF/EAC Kodovi po Standardu
├── Direktni IAF/EAC Kodovi (samo za Eksperte)
└── Raspored (Zakazani Auditi)
```

---

## Ključne Ozbake

### Statusi Sertifikata Kompanije
- **active** - Sertifikat je važi
- **suspended** - Privremena suspenzija
- **expired** - Sertifikat je istekao
- **pending** - Čeka se izdavanje
- **withdrawn** - Povučen od kompanije
- **cancelled** - Otkazan zbog nepoštovanja

### Statusi Audita
- **planned** - Planiran
- **scheduled** - Zakazan sa datumom
- **completed** - Završen
- **postponed** - Odložen

### Statusi Ciklusa
- **planned** - Planiran
- **ongoing** - U toku
- **completed** - Završen
- **suspended** - Suspenzija

---

## Automatske Akcije Sistema

1. **Isticanje Sertifikata**
   - Dashboard prikazuje upozorenja za 30, 60, 90 dana
   - Korisnici dobijaju notifikacije

2. **Validacija Auditora**
   - Sistem proverava dostupnost auditora
   - Sprečava dvostruke rezervacije

3. **Proračun Datuma**
   - Automatski dodaje 3 godine za istek
   - Izračunava dostupnost prostora

4. **Integrisan Audit**
   - Automatski detektuje više standarda
   - Smanjuje broj dana potrebnih

---

## Tipične Radne Procedure

### 1. Onboarding Nove Kompanije
1. Kreiraj kompaniju
2. Dodaj standarde
3. Dodaj IAF/EAC kodove
4. Dodaj kontakt osobe
5. Dodaj lokacije (ako trebaju)
6. Kreiraj inicijalni ciklus
7. Zakaži inicijalni audit
8. Dodeli auditory

### 2. Godišnja Nadzorna Provera
1. Kreiraj novi ciklus (Surveillance)
2. Odaberi iste standarde kao prethodno
3. Dodaj audit za svaki standard
4. Zakaži u kalendaru
5. Audit se odradi
6. Generiše izveštaj

### 3. Tri Godina - Revalidacija
1. Kreiraj novi ciklus (Recertification)
2. Odaberi standarde
3. Dodaj audite
4. Zakaži
5. Nakon audita, sertifikat se obrađuje
6. Datum isteka se ažurira

---

## Česte Greške i Rešenja

| Greška | Rešenje |
|--------|--------|
| "Obavezna polja" | Popunite sva polja sa * |
| "Auditor zauzet" | Odaberite drugi auditor ili datum |
| "Kod nije pronađen" | Kreirajte kod prvo ili odaberite od postojećih |
| "Kompanija već postoji" | Koristite pretragu, možda je već kreirana |

---

## Navigacijski Schnelkurse

### Počevši od Dashboard-a:
- **Na Kompanije:** Sidebar → Company List
- **Na Auditory:** Sidebar → Auditori
- **Na Kalendar:** Sidebar → Kalendar Sastanaka
- **Na Cikluse:** Sidebar → (prvi link koji vas odvede tamo)
- **Na IAF Kodove:** Sidebar → IAF/EAC Kodovi

### Vratiti se na Dashboard:
- Kliknite na "Dashboard" u Sidebar-u
- Ili "Početna" u logo klikanjem

---

## Korisne Informacije

### Format Datuma
- **Prikaz:** dd.mm.yyyy (npr. 25.12.2025)
- **Unos:** Koristi date picker ili pišite u formatu

### Format Broja Telefona
- **Format:** +381 10 234 5678 (sa kodom zemlje)
- **Ili:** 010 234 5678 (bez koda)

### Email
- **Validan:** primer@example.com
- **Nevalidan:** primer@, @example.com

---

## Šta Trebati Znati Pre Nego Što Počnete

1. **Matični broj kompanije** - 8 cifara
2. **PIB** - 8-9 cifara (opciono ali preporučeno)
3. **Standardи koje kompanija ima**
4. **IAF/EAC kodove** (ili mogu biti dodate kasnije)
5. **Imena kontakt osoba** (najmanje jedno)

---

## Korisni Saveti

1. **Pre kreiranja kompanije:** Prikupite sve potrebne podatke
2. **Standardna procedura:** Pročitajte tipične procedure prvo
3. **Drag-and-drop:** Super je za brzo premještanje audita
4. **Pretraga:** Koristi pretragu umesto ručnog pregledavanja
5. **Filtri:** Koristi filtere da restringijes šta vidiš
6. **Export:** Ako trebaju podaci, koristi Export funkciju

---

## Kontakt za Pomoć

**Problem?** Kontaktirajte administratora:
- Email: admin@example.com
- Telefon: +381 (11) 123-45-67

---

**IASOQAR v1.0** | Poslednja ažuriranja: 2025-01-15

