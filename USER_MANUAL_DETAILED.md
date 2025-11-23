# IASOQAR Aplikacija - Detaljni Korisnički Priručnik

## Sadržaj
1. [Uvod i Prijava](#uvod-i-prijava)
2. [Dashboard i Navigacija](#dashboard-i-navigacija)
3. [Kompanije - Upravljanje](#kompanije---upravljanje)
4. [Auditori - Upravljanje](#auditori---upravljanje)
5. [Sertifikacijski Ciklusi](#sertifikacijski-ciklusi)
6. [Kalendar i Zakazivanje](#kalendar-i-zakazivanje)
7. [IAF/EAC Kodovi](#iafеac-kodovi)
8. [Srbija Tim - Crni Kalendar](#srbija-tim---crni-kalendar)
9. [Lokacije](#lokacije)
10. [Kontakt Osobe](#kontakt-osobe)
11. [Dodatne Funkcionalnosti](#dodatne-funkcionalnosti)

---

## 1. UVOD I PRIJAVA

### 1.1 Prijava u Sistem

**URL:** `/accounts/login/`

#### Korak po Korak:
1. Otvorite aplikaciju na URL adresi `https://[domen]/accounts/login/`
2. Unesite korisničko ime u polje "Korisničko ime"
3. Unesite lozinku u polje "Lozinka"
4. Opciono: Označite "Zapamti me" ako želite da ostanete ulogovani
5. Kliknite na dugme "Prijava"

**Napomena:** Ako zaboravite lozinku, kontaktirajte administratora sistema.

#### Ekran Prijave Sadrži:
- Polje za korisničko ime
- Polje za lozinku
- Checkbox za "Zapamti me"
- Dugme "Prijava"
- Link za registraciju (ako je dozvoljeno)

---

## 2. DASHBOARD I NAVIGACIJA

### 2.1 Početna Stranica (Dashboard)

**URL:** `/dashboard/` ili `/company/dashboard/`

#### Struktura Dashboard-a

Dashboard je podeljen u **4 glavne kartice** sa statističkim podacima:

### **TAB 1: PREGLED (Glavne Metrike)**

#### Brzi Pregled - Redak 1:
| Metrika | Opis |
|---------|------|
| **Ukupno Kompanija** | Prikazuje ukupan broj registrovanih kompanija u sistemu |
| **Aktivni Sertifikati** | Broj kompanija sa aktivnim sertifikatima |
| **Auditi (30 Dana)** | Broj audita zakazanih u narednih 30 dana |
| **Neposlati Izveštaji** | Broj izveštaja iz Srbija Tim modula koji nisu poslati |

#### Brzi Pregled - Redak 2:
| Metrika | Opis |
|---------|------|
| **Sertifikati Ističu (30d)** | Broj sertifikata koji ističu u narednih 30 dana |
| **Ukupno Auditora** | Broj registrovanih auditora u sistemu |
| **Aktivni Ciklusi** | Broj aktivnih sertifikacijskih ciklusa |
| **Integrisani Sistemi** | Broj kompanija sa integrisanim sistemima (više standarda) |

#### Tabela: Sertifikati koji Ističu
- Prikazuje listu sertifikata koji ističu u narednih 30 dana
- Kolone: Kompanija, Standard, Broj Sertifikata, Datum Isticanja, Broj Dana, Akcije
- Akcije: Dugme za pregled detalja kompanije

### **TAB 2: KOMPANIJE - Statistika**

Detaljne statistike o kompanijama:

#### Status Kompanija:
1. **Ukupan Broj Kompanija** - Sve registrovane kompanije
2. **Aktivni Sertifikati** - Kompanije sa aktivnim sertifikatima (zeleno)
3. **Suspendovani** - Kompanije sa suspenzijom (žuto)
4. **Istekli** - Kompanije čiji su sertifikati istekli (sivo)
5. **Na Čekanju** - Kompanije u fazi čekanja (plavo)
6. **Deregistrovani** - Kompanije koje su deregistrovane (tamno)
7. **Otkazani** - Kompanije čiji su ciklusi otkazani (crno)

#### Isticanje Sertifikata:
- **Ističu (30 Dana)** - Crveno (hitno)
- **Ističu (60 Dana)** - Narandžasto (ubrzo)
- **Ističu (90 Dana)** - Plavo (budući period)
- **Već Istekli** - Sivo

### **TAB 3: AUDITI - Pregled Statusa**

Statistike o auditima:

#### Status Audita:
| Status | Opis |
|--------|------|
| **Planirani Auditi** | Auditi koji su planirani ali još nisu zakazani |
| **Zakazani Auditi** | Auditi koji su zakazani sa datumom i auditorima |
| **Završeni (Ovaj Mesec)** | Auditi završeni u tekućem mesecu |
| **Odloženi Auditi** | Auditi koji su odloženi |

#### Dodatne Metrike:
- **Auditi u Narednih 30 Dana** - Broj zakazanih audita
- **Prosečan Broj Dana po Auditu** - Izračunato iz aktivnih ciklusa
- **Ukupno Auditora** - Broj dostupnih auditora
- **Dostupni Danas** - Broj slobodnih auditora
- **Aktivni Ciklusi** - Broj aktivnih sertifikacijskih ciklusa
- **Integrisani Sistemi** - Broj kompanija sa više standarda

#### Tabela: Predstojeći Auditi (30 Dana)
Prikazuje detaljnu listu svih audita zakazanih u narednih 30 dana sa mogućnošću:
- Pregleda i izmene audita
- Pregleda detalja ciklusa
- Filtriranja po statusu i datumu

### **TAB 4: SRBIJA TIM - Crni Kalendar**

Statistike o posjetama Srbija Tim tima:

| Metrika | Opis |
|---------|------|
| **Zakazane (Ovaj Mesec)** | Broj zakazanih poseta ovaj mesec |
| **Odrađene (Ovaj Mesec)** | Broj završenih poseta ovaj mesec |
| **Poslati Izveštaji** | Broj poslanih izveštaja |
| **Neposlati Izveštaji** | Broj neposlanih izveštaja |

#### Tabela: Predstojeće Posete (7 Dana)
- Kompanija, Broj Sertifikata, Datum Posete, Auditori, Standardi, Status, Akcije

### 2.2 Glavna Navigacija

#### Gornja Navigacijska Traka (Navbar)

**Levo:**
- Hamburger Menu - Toggle sidebar
- **Kontrolna tabla** - Link na dashboard
- **Kompanije** - Link na listu kompanija
- **Kalendar** - Link na kalendar

**Desno:**
- **Korisnički Meni** - Kliknite na vaše korisničko ime
  - Prikazuje korisničko ime i datum učlanjenja
  - Opcije: Profil, Odjava

#### Levi Sidebar (Meni)

**ISOQAR** (Logo/Home)

**Stavke Menija:**

1. **Dashboard** 
   - Ikona: Brzinomer
   - Url: `/dashboard/`

2. **Kalendar Sastanaka** (NEW)
   - Ikona: Kalendar
   - Url: `/calendar/`
   - Opis: Interaktivni kalendar sa svim zakazanim auditorima i sastancima

3. **Company List**
   - Ikona: Lista
   - Url: `/companies/`
   - Opis: Pregled svih kompanija sa filtriranjem i pretraživanjem

4. **Auditori**
   - Ikona: Korisnici
   - Url: `/auditors/`
   - Opis: Upravljanje auditorima, njihovim standardima i IAF/EAC kodovima

5. **IAF/EAC Kodovi**
   - Ikona: Kod
   - Url: `/iaf-codes/`
   - Opis: Pregled svih dostupnih IAF/EAC kodova u sistemu

6. **Nadzorne Provere**
   - Ikona: Clipboard Check
   - Url: `/audits/`
   - Opis: Pregled svih audita

7. **Srbija Tim** (Submeni)
   - Ikona: Kalendar sa Check
   - **Kalendar** - Crni kalendar sa posjetama
   - **Raspored Auditora** - Pregled rasporeda auditora
   - **Lista Poseta** - Detaljna lista svih poseta

---

## 3. KOMPANIJE - UPRAVLJANJE

### 3.1 Prikaz Liste Kompanija

**URL:** `/companies/`

#### Struktura Stranice

**Zaglavlje:**
- Naslov: "Lista Kompanija"
- Dugme: "+ Nova Kompanija" (zeleno)

#### Funkcionalnosti Liste

**Pretraga i Filtriranje:**
- Polje za pretragu - Pretraživanje po: Imenu, PIB-u, Matičnom broju, IAF/EAC kodovima
- Filter po Statusu sertifikata
- Filter po datumima isteka sertifikata

**Tabela sa Kolonama:**
| Kolona | Sadržaj |
|--------|---------|
| Naziv | Naziv kompanije sa linkovi na detalje |
| Matični broj | MB kompanije |
| PIB | PIB kompanije |
| Industrija | Tip industrije |
| Standardi | Broj aktivnih standarda |
| Status | Status sertifikata (aktivan, suspenzija, istekao, itd.) |
| Akcije | Dugmići za: Pregled, Izmena, Brisanje |

**Boje Statusa:**
- 🟢 **Aktivan** - Zelena
- 🟡 **Suspenzija/Na čekanju** - Žuta
- 🔴 **Istekao/Otkazan** - Crvena
- ⚫ **Deregistrovan** - Siva

#### Akcije u Tabeli

| Dugme | Ikona | Akcija |
|-------|-------|--------|
| Pregled | Oko | Otvara stranicu sa detaljima kompanije |
| Izmena | Olovka | Otvara formu za izmenu kompanije |
| Brisanje | Kanta | Prikazuje potvrdu za brisanje |

### 3.2 Kreiranje Nove Kompanije

**URL:** `/companies/create/`

#### Korak po Korak

**Korak 1: Pristup**
1. Kliknite na dugme "+ Nova Kompanija" sa liste
2. Ili pristupite direktno na URL `/companies/create/`

**Korak 2: Popunjavanje Osnovih Podataka (TAB 1)**

Obavezna polja (označena sa *):
- **Naziv kompanije** *
- **Matični broj** *
- **Industrija** * (Dropdown sa opcijama)
- **Status sertifikata** * (active, suspended, expired, pending, withdrawn, cancelled)

Opciona polja:
- **PIB** - Poreski identifikacioni broj
- **Broj zaposlenih** - Broj zaposlenih u kompaniji
- **Telefon** - Kontakt telefon
- **Email** - Kontakt email
- **Website** - Website kompanije
- **Adresa** - Ulica, broj, mesto, poštanski broj
- **Napomene** - Dodatne napomene o kompaniji

**Korak 3: Dodavanje Standarda i Sertifikata (TAB 2)**

1. Kliknite na tab "Standardi i Sertifikati"
2. Sekcija "Podaci o sertifikatu":
   - **Broj sertifikata** - Uneti broj sertifikata kompanije
   - **Datum inicijalnog audita** - Datum prvog audita
   - **Suspenzija do datuma** - Ako je primenjiva
   - **Broj dana audita** - Koliko dana traje audit
   - **Poseta godišnje** - Broj godišnjih poseta
   - **Dana po auditu** - Prosečan broj dana
   - **Oblast registracije** - Detalji o oblasti

3. Tabela standarda:
   - Kliknite na "+ Dodaj Standard" dugme
   - Izaberite standard iz liste
   - Unesite datum izdavanja (automatski izračunava 3 godine za istok)
   - Unesite datum isteka (automatski popunjen)
   - Dodajte napomenu ako je potrebna

**Korak 4: Dodavanje IAF/EAC Kodova (TAB 3)**

1. Kliknite na tab "IAF/EAC Kodovi"
2. Kliknite na "+ Dodaj IAF/EAC kod"
3. Izaberite kod iz dostupne liste
4. Opciono: Označite kao primarni kod
5. Dodajte napomenu ako je potrebna

**Korak 5: Dodavanje Kontakt Osoba (TAB 4)**

1. Kliknite na tab "Kontakti"
2. Kliknite na "+ Dodaj Kontakt"
3. Unesite:
   - **Ime i Prezime** (obavezno)
   - **Pozicija** (obavezno)
   - **Email** (obavezno)
   - **Telefon** (obavezno)
4. Označite "Primarna kontakt osoba" ako je potrebna

**Korak 6: Dodavanje Lokacija (TAB 5)**

1. Kliknite na tab "Lokacije"
2. Kliknite na "+ Dodaj Lokaciju"
3. Unesite podatke o lokaciji (ulica, broj, grad, poštanski broj)

**Korak 7: Čuvanje**

1. Kliknite na dugme "Sačuvaj" na dnu stranice
2. Sistem će prikazati poruku o uspehu
3. Bićete prebačeni na stranicu sa detaljima kompanije

#### Obavezna Polja

Ako nije uneseno obavezno polje, sistem će prikazati:
- **Modalni prozor** sa listom obaveznih polja
- Kliknite na polje iz liste da biste prešli na odgovarajući tab

### 3.3 Pregled Detalja Kompanije

**URL:** `/companies/<company_id>/`

#### Struktura Stranice

**Zaglavlje:**
- Naziv kompanije
- Dugmići: Izmeni, Obriši, Nazad na listu

#### Kartice/Tabovi

**TAB 1: Osnovni Podaci**

Prikazuje u dve kolone:

**Leva kolona:**
- PIB
- Matični broj
- Adresa (ulica, broj, grad, poštanski kod)
- Telefon
- Email
- Website
- Industrija
- Status sertifikata
- Broj sertifikata
- Broj zaposlenih

**Desna kolona:**
- Oblast registracije
- Datum inicijalnog audita
- Broj poseta godišnje
- Broj dana po auditu
- Napomene

**TAB 2: Standardi i Sertifikati**

Tabela sa:
| Kolona | Opis |
|--------|------|
| Standard | Naziv standarda |
| Status | Status (Aktivan) |
| Datum izdavanja | Datum izdavanja sertifikata |
| Datum isteka | Datum isteka sertifikata |
| Auditori | Lista auditora zaduženih za standard |
| Akcije | Pregled, Izmena, Brisanje |

**TAB 3: IAF/EAC Kodovi**

Tabela sa:
| Kolona | Opis |
|--------|------|
| IAF/EAC kod | Kod |
| Opis | Opis koda |
| Status | Primarni (žuto) ili Sekundarni |
| Napomena | Dodatne napomene |

Akcije: Izmena, Brisanje, Postavi kao Primarni

**TAB 4: Kontakti**

Tabela sa:
| Kolona | Opis |
|--------|------|
| Ime i prezime | Naziv osobe |
| Pozicija | Radna pozicija |
| Email | Email adresa |
| Telefon | Telefon |
| Status | Primarna (zvezdica) ili sekundarna |

Akcije: Izmena, Brisanje

**TAB 5: Lokacije**

Tabela sa dodatnim lokacijama:
| Kolona | Opis |
|--------|------|
| Naziv | Naziv lokacije |
| Adresa | Kompletan adresa |
| Kontakt | Kontakt osoba (ako postoji) |

Akcije: Pregled, Izmena, Brisanje

**TAB 6: Provere i Auditi**

Tabela sa auditima za ovu kompaniju:
| Kolona | Opis |
|--------|------|
| Tip Audita | Initial, Surveillance, Recertification |
| Ciklus | Sertifikacijski ciklus kojem pripada |
| Datum | Planirani datum audita |
| Status | Planned, Scheduled, Completed, Postponed |
| Akcije | Pregled, Izmena |

**TAB 7: Sastanci**

Tabela sa zakazanim sastancima i događajima (ako postoje)

#### Dugmići na Stranici

**Gornji Desni Ugao:**
- **Izmeni** - Otvara formu za izmenu kompanije
- **Obriši** - Otvara potvrdu za brisanje
- **Nazad na listu** - Vraća na listu kompanija

### 3.4 Izmena Kompanije

**URL:** `/companies/<company_id>/update/`

**Proces:** Identičan kao kreiranje, ali sa pre-popunjenim poljima

### 3.5 Brisanje Kompanije

1. Na stranici sa detaljima kompanije, kliknite na dugme "Obriši"
2. Sistem će prikazati **potvrdu za brisanje**
3. Konfirmujte brisanje
4. Kompanija će biti obrisana iz sistema

---

## 4. AUDITORI - UPRAVLJANJE

### 4.1 Prikaz Liste Auditora

**URL:** `/auditors/`

#### Struktura Stranice

**Zaglavlje:**
- Naslov: "Auditori"
- Dugme: "+ Novi Auditor" (zeleno)

#### Tabela Auditora

| Kolona | Sadržaj |
|--------|---------|
| Ime i prezime | Nombre auditora |
| Email | Email adresa |
| Telefon | Kontakt telefon |
| Kategorija | Lead Auditor, Auditor, Tehnički ekspert, Trainer |
| Standardi | Broj standarda za koje je kvalifikovan |
| Akcije | Pregled, Izmena, Brisanje |

#### Boje Kategorija

- 🟢 **Lead Auditor** - Zelena
- 🔵 **Auditor** - Plava
- ⚫ **Tehnički ekspert** - Siva
- 🔷 **Trainer** - Svetloplava

### 4.2 Kreiranje Novog Auditora

**URL:** `/auditors/create/`

#### Osnovni Podaci (TAB 1)

Obavezna polja:
- **Ime i prezime** *
- **Email** *
- **Kategorija** * (Dropdown: Lead Auditor, Auditor, Tehnički ekspert, Trainer)

Opciona polja:
- **Telefon** - Kontakt telefon

#### Korak po Korak

1. Kliknite na "+ Novi Auditor"
2. Unesite ime i prezime
3. Unesite email adresu
4. Izaberite kategoriju auditora
5. Opciono: Dodajte telefon
6. Kliknite "Sačuvaj"

#### Obavezi

Napomena: "Nakon kreiranja auditora, moći ćete da dodate standarde i IAF/EAC kodove."

### 4.3 Pregled Detalja Auditora

**URL:** `/auditors/<auditor_id>/`

#### Struktura

**Zaglavlje:**
- Ime auditora sa kategorijom kao badge (boja zavisi od kategorije)
- Dugmići: Nazad, Izmeni, Obriši

**TAB 1: Osnovne Informacije**

- Ime i prezime
- Email
- Telefon
- Kategorija

**TAB 2: Standardi**

Tabela sa standardima za koje je auditor kvalifikovan:

| Kolona | Opis |
|--------|------|
| Standard | Naziv standarda |
| IAF/EAC Kodovi | Lista kodova za ovaj standard |
| Akcije | Izmena, Brisanje |

Dugme: "+ Dodaj Standard"

#### Dodavanje Standarda Auditor

1. Kliknite "+ Dodaj Standard"
2. Izaberite standard iz liste dostupnih standarda
3. Kliknite "Sačuvaj"
4. Sada možete dodati IAF/EAC kodove za ovaj standard

**Dodavanje IAF/EAC kodova za Standard:**
1. U tabeli standarda, na redu odgovarajućeg standarda, kliknite "+ Dodaj IAF/EAC kod"
2. Izaberite jedan ili više IAF/EAC kodova iz liste
3. Kliknite "Sačuvaj"

#### Za Tehničke Eksperte - Direktni IAF/EAC Kodovi

Ako je auditor "Tehnički ekspert", može imati direktno dodeljene IAF/EAC kodove bez standarda:

**Tabela: Direktni IAF/EAC Kodovi**
- Ista kao standardi, ali bez vezanog standarda
- Akcije: Izmena, Brisanje
- Dugme: "+ Dodaj Direktni IAF/EAC kod"

**Proces:**
1. Kliknite "+ Dodaj Direktni IAF/EAC kod"
2. Izaberite jedan ili više kodova
3. Kliknite "Sačuvaj"

### 4.4 Izmena i Brisanje Auditora

- **Izmena:** URL `/auditors/<auditor_id>/update/` - Identično kao kreiranje
- **Brisanje:** Dugme "Obriši" na stranici sa detaljima

---

## 5. SERTIFIKACIJSKI CIKLUSI

### 5.1 Prikaz Liste Ciklusa

**URL:** `/cycles/`

#### Zaglavlje

- Naslov: "Ciklusi Sertifikacije"
- Breadcrumb: Početna → [Kompanija] → Ciklusi
- Dugme: "+ Novi Ciklus"

#### Filtriranje i Pretraga

Dostupni filteri:
- **Pretraga** - Po nazivu kompanije
- **Status** - Dropdown sa statusima (planned, ongoing, completed, suspended)
- **Sortiranje** - Po datumu (najnoviji/najstariji), po statusu

#### Tabela

| Kolona | Sadržaj |
|--------|---------|
| Kompanija | Naziv kompanije sa linkovi na detalje |
| Status | Status ciklusa |
| Planirani datum | Datum planiranog početka |
| Standardi | Broj standarda obuhvaćenih |
| Integrisani sistem | Da/Ne (ima li više od 1 standarda) |
| Auditi | Broj planiranih audita |
| Akcije | Pregled, Izmena, Brisanje |

### 5.2 Kreiranje Novog Ciklusa

**URL:** `/cycles/create/` ili `/companies/<company_id>/cycles/create/`

#### Osnovne Informacije

Obavezna polja:
- **Kompanija** * (Ako nije unapred izabrana)
- **Tip ciklusa** * (Initial, Surveillance, Recertification)
- **Planirani datum** * (Datum početka ciklusa)
- **Broj dana audita** * (Ukupan broj dana za sve audite u ciklusu)

Opciona polja:
- **Status** - (planned, ongoing, completed, suspended)
- **Napomene** - Dodatne napomene

#### Korak po Korak

1. Kliknite "+ Novi Ciklus"
2. Izaberite kompaniju (ako nije unapred izabrana)
3. Izaberite tip ciklusa
4. Unesite planirani datum
5. Unesite ukupan broj dana za audite
6. Kliknite "Sačuvaj"

### 5.3 Pregled Detalja Ciklusa

**URL:** `/cycles/<cycle_id>/`

#### Struktura

**Zaglavlje sa Informacijama:**
- Naziv kompanije
- Status ciklusa
- Planirani datum
- Tip ciklusa

#### Kartice/Tabovi

**TAB 1: Osnovni Podaci**

- Kompanija (Link)
- Tip ciklusa
- Status
- Planirani datum
- Broj dana audita
- Napomene

**TAB 2: Standardi**

Tabela sa standardima obuhvaćenim u ovom ciklusu:

| Kolona | Opis |
|--------|------|
| Standard | Naziv |
| Scope | Oblast primene |
| Auditori | Dodelјeni auditori |
| Akcije | Pregled, Izmena, Brisanje |

**TAB 3: Auditi**

Tabela sa svim auditima u ciklusu:

| Kolona | Opis |
|--------|------|
| Redni broj | Redosled audita (1, 2, 3...) |
| Tip | Vrsta audita (initial, surveillance, itd.) |
| Planirani datum | Datum |
| Vodeći auditor | Ime auditora |
| Status | Planned, Scheduled, Completed, Postponed |
| Broj dana | Trajanje audita |
| Akcije | Pregled, Izmena, Brisanje |

**Dodavanje Audita:**
1. Kliknite "+ Dodaj Audit"
2. Popunite:
   - Tip audita
   - Planirani datum
   - Vodeći auditor
   - Broj dana
   - Dodatne auditors (ako potrebno)
3. Kliknite "Sačuvaj"

#### Informativne Kutije

**Statistika Ciklusa:**
- Broj standarda
- Broj audita
- Ukupno dana auditiranja
- Status ciklusa

### 5.4 Izmena i Brisanje Ciklusa

- **Izmena:** URL `/cycles/<cycle_id>/update/`
- **Brisanje:** Potvrda pri kliku na "Obriši"

---

## 6. KALENDAR I ZAKAZIVANJE

### 6.1 Kalendar Sastanaka

**URL:** `/calendar/`

#### Struktura Stranice

**Zaglavlje:**
- Naslov: "Kalendar Sastanaka"
- Datum/Pregled selektor

**Glavni Sadržaj:**
- **Interaktivni Kalendar** sa FullCalendar bibliotekom
- Prikazi: Mesečni, Nedeljni, Dnevni
- Mogućnost drag-and-drop premještanja događaja

#### Tipovi Događaja

Događaji se prikazuju različitim bojama:
1. **Auditi** - Plava boja
2. **Održavanje** - Narandžasta boja
3. **Otkazano** - Siva boja

#### Interakcije sa Kalendarem

**Kreiranje Novog Događaja:**
1. Kliknite na dan u kalendaru
2. Otvorit će se modal za kreiranje
3. Popunite:
   - Naziv (automatski preuzeto iz ciklusa)
   - Datum početka
   - Datum završetka
   - Vodeći auditor
   - Dodatni auditori
4. Kliknite "Sačuvaj"

**Drag-and-Drop:**
1. Kliknite i držite na događaj
2. Povučite na novi dan
3. Sistem će automatski ažurirati datum
4. Prikazat će se potvrda

**Pregled Detalja Događaja:**
1. Kliknite na događaj u kalendaru
2. Otvorit će se modal sa detaljima
3. Možete ažurirati:
   - Datum
   - Auditory
   - Status
   - Napomene

**Brisanje Događaja:**
1. Kliknite na događaj
2. U modalu, kliknite "Obriši"
3. Potvrdite brisanje

#### Filtriranje Događaja

- Prikazi samo određene tipove audita
- Filtriranje po auditorima
- Filtriranje po kompanijama
- Filtriranje po statusu

### 6.2 Detaljni Pregled Sastanka

**URL:** `/appointments/<appointment_id>/`

#### Struktura

| Polje | Opis |
|-------|------|
| Naziv | Naziv sastanka/audita |
| Kompanija | Naziv kompanije |
| Datum Početka | Datum i vreme početka |
| Datum Završetka | Datum i vreme završetka |
| Vodeći auditor | Ime auditora |
| Dodatni auditori | Dodatni auditora na auditu |
| Status | Planned, Scheduled, Completed |
| Napomene | Dodatne napomene |
| Lokacija | Lokacija (ako je navedena) |

#### Akcije

- **Izmeni** - Otvara formu za izmenu
- **Obriši** - Briše sastanak
- **Nazad** - Vraća na kalendar

---

## 7. IAF/EAC KODOVI

### 7.1 Prikaz Liste IAF/EAC Kodova

**URL:** `/iaf-codes/`

#### Struktura Stranice

**Zaglavlje:**
- Naslov: "IAF/EAC Kodovi"
- Statistika: Ukupno kodova, Aktivnih, Deaktiviranih

#### Tabela

| Kolona | Sadržaj |
|--------|---------|
| IAF Kod | Kod u formatu (npr. A01, A01.01) |
| Opis | Detaljan opis areas |
| Kategorija | Tip koda (Management, Environmental, itd.) |
| Status | Aktivan/Neaktivan |
| Broj Kompanija | Koliko kompanija koristi kod |
| Broj Auditora | Koliko auditora je kvalifikovano |

#### Pretraga

- Polje za pretragu po kodu
- Filtriranje po kategoriji
- Filtriranje po statusu

### 7.2 Upravljanje IAF/EAC Kodovima

**Za Kompanije:** IAF/EAC kodovi se dodeljuju preko stranice kompanije u TAB-u "IAF/EAC Kodovi"

**Za Auditory:** IAF/EAC kodovi se dodeljuju preko stranice auditora kao deo standarda ili direktno (za tehničke eksperte)

#### Dodavanje Koda Kompaniji:

1. Otvorite stranicu kompanije
2. Idite na tab "IAF/EAC Kodovi"
3. Kliknite "+ Dodaj IAF/EAC kod"
4. Iz liste dostupnih kodova, izaberite željeni kod
5. Opciono:
   - Označite kao "Primarni kod"
   - Dodajte napomenu
6. Kliknite "Sačuvaj"

#### Postavljanje Primarnog Koda

1. U tabeli kodova kompanije, kliknite na ikonicu zvezdice pored koda
2. Sistem će postaviti taj kod kao primarni
3. Primarni kod se prikazuje sa žutom bojom

---

## 8. SRBIJA TIM - CRNI KALENDAR

### 8.1 Kalendar Srbija Tim-a

**URL:** `/srbija-tim/` (kalendar)

#### Struktura

**Zaglavlje:**
- Naslov: "Srbija Tim - Crni Kalendar"
- Dugme: "+ Nova Poseta"
- Dugme: "Lista Poseta"

**Kalendar:**
- Interaktivni kalendar sa bojama za različite statuse
- Mogućnost drag-and-drop (ako je primenjivo)

#### Legenda

| Boja | Status |
|------|--------|
| 🔵 Plava | Zakazan |
| 🟢 Zelena | Odrađena |
| 🟡 Žuta | Na čekanju |
| ⚫ Siva | Otkazano |

### 8.2 Lista Poseta Srbija Tim-a

**URL:** `/srbija-tim/list/`

#### Struktura

**Zaglavlje:**
- Naslov: "Lista Poseta"
- Dugme: "Kalendar" (Nazad)
- Dugme: "+ Nova Poseta"

**Pretraga:**
- Polje za pretragu po: Broju sertifikata, Nazivu firme, Standardima, Auditorima

#### Tabela

| Kolona | Sadržaj |
|--------|---------|
| Broj sertifikata | Broj sertifikata |
| Kompanija | Naziv kompanije |
| Datum posete | Datum zakazane posete |
| Vreme | Vreme posete |
| Auditori | Imena auditora |
| Standardi | Standardi koje trebalo da se auditiraju |
| Status | Zakazan, Odrađen, Otkazan |
| Izveštaj poslat | Da/Ne |
| Akcije | Pregled, Izmena, Brisanje |

### 8.3 Kreiranje Nove Posete

**URL:** `/srbija-tim/create/`

#### Osnovne Informacije

Obavezna polja:
- **Broj sertifikata** * (Unique identifikator)
- **Kompanija** * (Automatski preuzeto ako je unesen broj sertifikata)
- **Datum posete** * (Datum zakazane posete)
- **Vreme** (Vreme početka posete, opciono)

#### Izbor Auditora i Standarda

**Auditori:**
- Polje za izbor: Jedan ili više auditora iz liste dostupnih
- Select2 widget sa pretragom

**Standardi:**
- Polje za izbor: Jedan ili više standarda koje trebalo da se auditiraju
- Select2 widget sa pretragom

#### Dodatne Informacije

- **Status** - Zakazan, Odrađen, Otkazan
- **Napomene** - Dodatne napomene o poseti
- **Izveštaj poslat** - Checkbox da li je izveštaj poslat

#### Korak po Korak

1. Kliknite "+ Nova Poseta"
2. Unesite broj sertifikata
3. Automatski će biti preuzeta kompanija
4. Izaberite auditory
5. Izaberite standarde
6. Izaberite datum i vreme
7. Unesite status
8. Opciono: Dodajte napomene
9. Kliknite "Sačuvaj"

### 8.4 Raspored Auditora

**URL:** `/srbija-tim/auditor-schedule/`

#### Struktura

**Zaglavlje:**
- Naslov: "Raspored Auditora"

**Tabela:**

| Kolona | Opis |
|--------|------|
| Auditor | Ime auditora |
| Broj Zakazanih | Broj zakazanih poseta |
| Broj Završenih | Broj završenih poseta |
| Broj Pendinga | Broj poseta na čekanju |
| Slobodnih Dana | Broj slobodnih dana |
| Akcije | Pregled rasporeda |

#### Individualni Raspored Auditora

1. Kliknite na auditora iz tabele
2. Prikazat će se njegov raspored za mesec
3. Viđate na kojima je danima zakazan

---

## 9. LOKACIJE

### 9.1 Prikaz Liste Lokacija

**URL:** `/locations/`

#### Struktura

**Zaglavlje:**
- Naslov: "Lokacije"
- Dugme: "+ Nova Lokacija"

#### Tabela

| Kolona | Sadržaj |
|--------|---------|
| Naziv | Naziv lokacije |
| Kompanija | Kompanija kojem pripada |
| Adresa | Kompletan adresa |
| Grad | Grad |
| Poštanski kod | Poštanski kod |
| Akcije | Pregled, Izmena, Brisanje |

### 9.2 Kreiranje Nove Lokacije

**URL:** `/locations/create/`

#### Osnovni Podaci

Obavezna polja:
- **Kompanija** * (Dropdown)
- **Naziv lokacije** * (Naziv)
- **Adresa** * (Ulica i broj)
- **Grad** * (Naziv grada)
- **Poštanski kod** * (Poštanski kod)

Opciona polja:
- **Kontakt osoba** (Ime osobe)
- **Telefon** (Telefon lokacije)
- **Email** (Email lokacije)
- **Napomene** (Dodatne napomene)

#### Korak po Korak

1. Kliknite "+ Nova Lokacija"
2. Izaberite kompaniju
3. Unesite naziv lokacije
4. Unesite adresu (ulica, broj)
5. Unesite grad
6. Unesite poštanski kod
7. Opciono: Dodajte kontakt podatke
8. Kliknite "Sačuvaj"

### 9.3 Pregled i Izmena Lokacija

**URL:** `/locations/<location_id>/`

Prikazuje sve podatke o lokaciji sa mogućnošću izmene ili brisanja.

---

## 10. KONTAKT OSOBE

### 10.1 Upravljanje Kontakt Osoba

Kontakt osobe se kreiraju i upravljaju kroz stranicu kompanije.

#### Kreiranje Kontakt Osobe

1. Otvorite stranicu kompanije
2. Idite na tab "Kontakti"
3. Kliknite "+ Dodaj Kontakt"
4. Popunite:
   - **Ime i prezime** * (obavezno)
   - **Pozicija** * (obavezno)
   - **Email** * (obavezno)
   - **Telefon** * (obavezno)
   - **Primarna osoba** (Checkbox - da li je primarna)
5. Kliknite "Sačuvaj"

#### Izmena Kontakt Osobe

1. U tabeli kontakt osoba kompanije, kliknite na dugme "Izmeni"
2. Izmenite željene podatke
3. Kliknite "Sačuvaj"

#### Brisanje Kontakt Osobe

1. U tabeli kontakt osoba, kliknite na dugme "Obriši"
2. Potvrdite brisanje

---

## 11. DODATNE FUNKCIONALNOSTI

### 11.1 Drag-and-Drop u Kalendaru

**Kako funkcionira:**

1. U kalendaru, pronađite događaj
2. Kliknite i držite miš na događaju
3. Povucite događaj na novi dan
4. Otpustite miš
5. Sistem će automatski:
   - Ažurirati datum događaja
   - Prikazati potvrdu
   - Ažurirati sve relevantne veze

**Ograničenja:**
- Možete premještati samo svoje događaje (ili ako imate permissions)
- Sistem će prikazati grešku ako je dan zauzet

### 11.2 Pretraga i Filtriranje

#### Pretraga Kompanija

- Po imenu
- Po PIB-u
- Po matičnom broju
- Po IAF/EAC kodovima
- Po datumima isteka sertifikata

#### Filtriranje Audita

- Po statusu
- Po datumu
- Po auditori
- Po kompaniji
- Po tipu audita

### 11.3 Eksportovanje Podataka

Gde je dostupno:
- Dugme "Eksportuj" (Excel, PDF, CSV)
- Obično se nalazi u toolbar-u tabela

### 11.4 Obaveštenja

Sistem prikazuje obaveštenja:
- **Zelena** - Uspešna akcija
- **Crvena** - Greška
- **Žuta** - Upozorenje
- **Plava** - Informacija

### 11.5 Pregled历史

Dostupno za:
- Izmene kompanija
- Izmene auditora
- Izmene ciklusa

Prikazuje:
- Šta je promenjeno
- Ko je promenio
- Kada je promenjeno

---

## ČESTI PROBLEMI I REŠENJA

### Problema: "Obavezna polja nisu popunjena"

**Rešenje:**
1. Pojavit će se modalni prozor sa listom obaveznih polja
2. Kliknite na polje u listi
3. Biće prebačeni na odgovarajući tab
4. Popunite nedostajuće podatke

### Problema: "Auditor se već koristi"

**Rešenje:**
- Sistem ne dozvoljava brisanje auditora koji je vezan za budućie audite
- Prvo otkaži sve budućie audite sa ovim auditorom

### Problema: "Greška pri čuvanju"

**Rešenje:**
1. Proverite da li su sva obavezna polja popunjena
2. Proverite format podataka (datumi, email, telefon)
3. Osvežite stranicu (F5)
4. Pokušajte ponovo

---

## TIPSKE RADNE PROCEDURE

### Procedura: Kreiranje Novog Sertifikacijskog Ciklusa

1. Otvorite listu kompanija
2. Pronađite kompaniju
3. Kliknite na kompaniju
4. Na stranici detalja, kliknite "+ Dodaj Ciklus"
5. Popunite:
   - Tip ciklusa (Initial, Surveillance, Recertification)
   - Planirani datum
   - Broj dana
6. Kliknite "Sačuvaj"
7. Sada dodajte standarde za ciklus
8. Dodajte audite sa datumima i auditorima
9. Zakazite audite u kalendaru

### Procedura: Dodela Auditora Kompaniji

1. Otvorite stranicu kompanije
2. Idite na tab "Standardi"
3. Za svaki standard, prikazat će se lista dostupnih auditora
4. Auditori su već povezani preko svoje kvalifikacije na standardima
5. Ako trebate drugog auditora, prvo ga trebate kvalifikovati na standardu

### Procedura: Ažuriranje Status Sertifikata

1. Otvorite stranicu kompanije
2. Kliknite "Izmeni"
3. Promenije "Status sertifikata"
4. Kliknite "Sačuvaj"
5. Status će biti ažuriran na dashboard-u

---

## PREČICE I TIPKE

| Akcija | Opis |
|--------|------|
| Ctrl+S | Čuvanje (na većini formi) |
| Escape | Zatvaranje modala |
| Tab | Premještanje između polja |
| Enter | Potvrda forme |

---

## KONTAKT I PODRŠKA

Za dodatnu pomoć ili prijavu problema:
- Kontaktirajte administratora sistema
- Email: [admin@example.com]
- Telefon: [broj telefona]

---

**Verzija Dokumenta:** 1.0
**Datum Kreiranja:** 2025-01-01
**Zadnja Ažuriranja:** 2025-01-01


---

# DETALJNE FUNKCIONALNOSTI PO SEKCIJI

## A. KOMPANIJE - DETALJAN PREGLED

### A.1 Kreiranje Kompanije - Detaljni Koraci

#### FAZA 1: OSNOVNI PODACI

**Obavezna Polja:**

1. **Naziv kompanije** (tekst)
   - Uneti puno naziv kompanije
   - Primer: "Fabrika Elektronike d.o.o. Beograd"
   - Ovo polje se koristi u svim izveštajima i dokumentima

2. **Matični broj** (broj)
   - 8-cifren broj iz registra
   - Primer: "12345678"
   - Jedinstveno identifikuje kompaniju

3. **Industrija** (dropdown)
   - Dostupne opcije:
     * Manufacturing (Proizvodnja)
     * Services (Usluge)
     * Construction (Građevinarstvo)
     * IT (Informacione tehnologije)
     * Other (Ostalo)
   - Koristi se za kategorizaciju i analizu

4. **Status sertifikata** (dropdown)
   - **active** - Aktivan sertifikat
   - **suspended** - Privremeno suspenzija
   - **expired** - Sertifikat je istekao
   - **pending** - U procesu prihvatanja
   - **withdrawn** - Povučen od strane kompanije
   - **cancelled** - Otkazan zbog nepoštovanja standarda

**Opciona Polja:**

- **PIB** - Poreski identifikacioni broj (8-9 cifara)
- **Broj zaposlenih** - Numerička vrednost
- **Telefon** - Format: +381 XX XXX XXXX
- **Email** - Validan email format
- **Website** - URL veba kompanije
- **Adresa** - Ulica, broj (OBAVEZAN deo)
- **Grad** - Naziv grada (OBAVEZAN deo)
- **Poštanski kod** - Postanski kod (OBAVEZAN deo)
- **Napomene** - Besplatan tekst za dodatne informacije

#### FAZA 2: SERTIFIKATI I STANDARDI

**Sekcija: Podaci o Sertifikatu**

| Polje | Tip | Opis |
|-------|-----|------|
| Broj sertifikata | Tekst | Jedinstveni broj sertifikata (npr. SAI-001234) |
| Datum inicijalnog audita | Datum | Datum prvog audita (obavezno za pravni trag) |
| Suspenzija do datuma | Datum | Ako je primenjiva suspenzija |
| Broj dana audita | Broj | Koliko dana traju godišnji auditi |
| Poseta godišnje | Broj | Broj godišnjih poseta auditora |
| Dana po auditu | Broj (decimala) | Prosečan broj dana po auditu |
| Oblast registracije | Tekst | Detaljni opis oblasti primene |

**Dodavanje Standarda:**

1. Kliknite na dugme "+ Dodaj Standard" u tabeli
2. Bira se standard iz liste dostupnih:
   - ISO 9001:2015 (Sistem upravljanja kvalitetom)
   - ISO 14001:2015 (Sistem upravljanja zaštitom okoline)
   - ISO 45001:2018 (Sistem upravljanja sigurnosti i zdravlje na radu)
   - ISO 50001:2018 (Sistem upravljanja energijom)
   - IATF 16949:2016 (Automobilska industrija)
   - AS9100 (Aerokosmička industrija)
   - Ostali relevantni standardi

3. **Datum izdavanja** - Kada je sertifikat izdat
   - Automatski izračunava se datum isteka (3 godine od izdavanja)
4. **Datum isteka** - Automatski se popunjava
5. **Napomena** - Opciona polja za specifične napomene

**Automatski Proračun Datuma Isteka:**
- Sistem automatski dodaje 3 godine na datum izdavanja
- Datum se prikazuje u formatu dd.mm.yyyy
- Može se ručno izmeniti ako je potrebno

#### FAZA 3: IAF/EAC KODOVI

**Šta su IAF/EAC Kodovi?**
- Kodovi koji označavaju specifičnu oblast primene sertifikata
- Format: A01, A01.01, B01, B02.01 itd.
- Svaki kod ima detaljan opis domene

**Dodavanje Kodova:**

1. Kliknite "+ Dodaj IAF/EAC kod"
2. Iz dropdown liste izaberite kod(ove)
3. Opciono: Označite kao **Primarni kod**
   - Samo jedan kod može biti primarni
   - Prikazuje se sa žutom bojom
4. Opciono: Dodajte napomenu o kodu
5. Kliknite "Sačuvaj"

**Primer IAF/EAC Kodova:**
- A01 - All activities
- A01.01 - Design, development and engineering
- A01.02 - Production and delivery of goods/services
- B - Test and Calibration laboratories
- C - Inspection Bodies

#### FAZA 4: KONTAKT OSOBE

**Obavezna Polja:**
- **Ime i prezime**
- **Pozicija** (Direktor, Manager Kvaliteta, itd.)
- **Email** - Validan email
- **Telefon** - Telefon osobe

**Primarna Kontakt Osoba:**
- Označava se sa zvezdikom
- Samo jedna osoba može biti primarni kontakt
- Koristi se za prvi kontakt i važne komunikacije

**Tipične Pozicije:**
- Direktor - Rukovodilac preduzeća
- Manager Kvaliteta - Odgovoran za sistem kvaliteta
- Manager Okoline - Odgovoran za zaštitu okoline
- Manager Sigurnosti - Odgovoran za sigurnost na radu
- Tehnički Direktor - Odgovoran za tehničke aspekte

#### FAZA 5: LOKACIJE

**Dodavanje Dodatnih Lokacija:**

Ako kompanija ima više lokacija (fabrike, kancelarije, skladišta), svaku lokaciju trebati dodati odvojeno.

1. Kliknite "+ Dodaj Lokaciju"
2. Popunite:
   - Naziv lokacije (npr. "Fabrika Beograd", "Magacin Zemun")
   - Adresa (ulica i broj)
   - Grad
   - Poštanski kod
3. Opciono:
   - Kontakt osoba na toj lokaciji
   - Telefon lokacije
   - Email lokacije

**Важне Napomene:**
- Glavna lokacija je ona gde će se održavati auditi
- Dodatne lokacije mogu biti uključene u scope sertifikata

---

### A.2 Pregled Kompanije - Detaljne Informacije

Na stranci sa detaljima kompanije mogu se videti svi važni podaci strukturirani u kartice:

#### INFO TABELA - Osnovni Podaci

Prikazuje ključne informacije o kompaniji u formatiranoj tabeli:
- PIB i Matični broj za lakšu identifikaciju
- Kompletan adresa
- Kontakt podaci
- Industrija
- Status sertifikata

#### TABELA STANDARDA

Prikazuje sve standarde za koje je kompanija sertifikovana:

| Informacija | Opis |
|-------------|------|
| Standard | Naziv standarda (ISO 9001, ISO 14001, itd.) |
| Status | Uvek "Aktivan" na stranici detalja (neaktivni se ne prikazuju) |
| Datum izdavanja | Kada je sertifikat izdat |
| Datum isteka | Važno za praćenje isteka |
| Auditori | Lista auditora dodelјenih za ovaj standard |
| Akcije | Pregled, Izmena, Brisanje standarda |

**Akcije na Standardu:**

1. **Pregled** (Oko ikonita)
   - Prikazuje sve detalje standarda
   - IAF/EAC kodove koji se primenjuju
   - Istoriju audita za ovaj standard

2. **Izmena** (Olovka ikonita)
   - Ažurira podatke o standardu
   - Može se promeniti datum isteka
   - Mogu se dodati nove napomene

3. **Brisanje** (Kanta za otpad ikonita)
   - Briše standard iz kompanije
   - Potrebna potvrda
   - Uticaj: Broji se kao manje standarda na dashboard-u

#### TABELA IAF/EAC KODOVA

Prikazuje sve dodeljene kodove:

| Kolona | Opis |
|--------|------|
| IAF/EAC kod | Kod u formatu (A01, B02.01, itd.) |
| Opis | Detaljan opis domene |
| Status | Primarni (žuta boja) ili sekundarni |
| Napomena | Dodatne napomene o kodu |

**Upravljanje Kodovima:**

- Postavi kao Primarni - Žuta boja
- Izmeni - Menja napomenu
- Obriši - Uklanja kod iz kompanije

#### TABELA KONTAKT OSOBA

Prikazuje sve registrovane kontakt osobe:

| Kolona | Opis |
|--------|------|
| Ime i prezime | Imena kontakt osoba |
| Pozicija | Njihova pozicija |
| Email | Email za komunikaciju |
| Telefon | Telefon osobe |
| Status | Primarna (sa zvezdikom) |

#### TABELA LOKACIJA

Sve dodatne lokacije kompanije sa adresama i kontaktima.

#### TABELA PROVERE I AUDITI

Prikazuje sve audite koje je kompanija imala:

| Kolona | Opis |
|--------|------|
| Tip | Initial, Surveillance, Recertification |
| Ciklus | Kojem ciklusu pripada |
| Datum | Kada je audit odrađen |
| Status | Completed, Scheduled, Planned, Postponed |
| Akcije | Pregled i izmena |

#### TABELA SASTANCI

Zakazani sastanci sa auditorima (ako postoje).

---

## B. AUDITORI - DETALJAN PREGLED

### B.1 Kategorije Auditora

#### 1. **Lead Auditor** (Vodeći Auditor)
- Ikona: Zelena boja
- Uloga: Vodi audit, odgovoran je za sve procedurale
- Kvalifikacija: Mora imati specijalizovanu obuku
- Na auditima: Bar jedan Lead Auditor mora biti prisutan
- Primer: "Marko Marković - Lead Auditor ISO 9001"

#### 2. **Auditor** (Redovni Auditor)
- Ikona: Plava boja
- Uloga: Izvršava audit pod vođstvom Lead Auditora
- Kvalifikacija: Obučen za specifičan standard
- Na auditima: Mogu raditi sa Lead Auditorom
- Primer: "Ana Anić - Auditor ISO 9001"

#### 3. **Technical Expert** (Tehnički Ekspert)
- Ikona: Siva boja
- Uloga: Daje stručnu ocenu specifičnih delova
- Kvalifikacija: Duboka tehnička znanja
- Na auditima: Angažovan po potrebi
- Primer: "Petar Petrović - Technical Expert QMS"

#### 4. **Trainer** (Instruktor)
- Ikona: Svetloplava boja
- Uloga: Obučava kompanije na standardima
- Kvalifikacija: Obučavač sa sertifikatom
- Na auditima: Ne učestvuje direktno
- Primer: "Jovan Jovanović - Trainer ISO 14001"

### B.2 Dodela Standarda Auditorima

**Koji su Standardi Dostupni:**

Svi standardi u sistemu (isti kao za kompanije):
- ISO 9001:2015
- ISO 14001:2015
- ISO 45001:2018
- ISO 50001:2018
- IATF 16949:2016
- AS9100
- Ostali

**Proces Dodele:**

1. Otvorite profil auditora
2. U tab-u "Standardi", kliknite "+ Dodaj Standard"
3. Izaberite standard
4. Potvrdi se dodela
5. Sada auditor ima pristup svim kompanijama sa ovim standardom

### B.3 IAF/EAC Kodovi za Auditory

**Za Regularne Auditory:**

Kodovi se dodeljuju kao deo standarda:
1. Odaberite standard koji auditor ima
2. U tabeli standarda, kliknite "+ Dodaj IAF/EAC kod"
3. Izaberite kodove koji se odnose na ovaj standard
4. Sada auditor može auditirati kompanije sa ovim kodovima

**Za Tehničke Eksperte:**

Mogu imati direktne kodove bez standarda:
1. U tab-u "Direktni IAF/EAC Kodovi"
2. Kliknite "+ Dodaj Direktni IAF/EAC kod"
3. Izaberite kodove
4. Tehnički ekspert sada ima pristup ovim domenama

**Primer:**
- Auditor ima ISO 9001
- Za ISO 9001, kodovi su: A01 (Design), A01.02 (Production), B03 (Services)
- Auditor sada može auditirati sve kompanije sa ovim kodovima

### B.4 Raspored i Dostupnost Auditora

**Kako Sistem Prati Dostupnost:**

1. Svaki auditor ima raspored na kalendaru
2. Kada se audit zakazuje, auditor se rezerviše
3. Sistem automatski proverava dostupnost
4. Ne mogu se zakazati dva audita u istom periodu
5. Sistem prikazuje upozorenje ako postoji konflikt

**Prikazivanje Dostupnosti:**

Na dashboard-u:
- "Dostupni Danas" - Broj auditora dostupnih danasnje
- "Najzauzetiji Auditor" - Ko ima najviše audita ovaj mesec
- "Prosečan Broj Dana po Auditu" - Za planiranje

---

## C. SERTIFIKACIJSKI CIKLUSI - DETALJNO

### C.1 Tipovi Ciklusa

#### 1. **Initial Audit** (Inicijalni Audit)
- Prvi audit kompanije
- Obavezno treba da se izvrši
- Trajanje: Obično 3-5 dana
- Rezultat: Sertifikat

#### 2. **Surveillance Audit** (Nadzorna Provera)
- Godišnja provera da se drži standard
- Obavezna svake godine
- Trajanje: 1-2 dana
- Rezultat: Potvrda validnosti sertifikata

#### 3. **Recertification Audit** (Revalidacija)
- Sprovodi se svake 3 godine (pre isteka sertifikata)
- Obavezna za očuvanje sertifikata
- Trajanje: 2-3 dana
- Rezultat: Novi sertifikat (još 3 godine)

### C.2 Faze Ciklusa

#### Faza 1: Kreiranje Ciklusa
- Unese se osnovni podaci
- Skupa se plan ciklusa

#### Faza 2: Definisanje Standarda
- Selektuju se standardi koje će audit pokrivati
- Može biti jedan ili više standarda (Integrated Audit)

#### Faza 3: Planiranje Audita
- Planira se broj audita u ciklusu
- Obično: 1 auditor (za Initial), 1 auditor (za Surveillance), 1-2 (za Recertification)

#### Faza 4: Zakazivanje Audita
- Definišu se datumi audita
- Dodeljuju se auditori
- Sistem proverava njihovu dostupnost

#### Faza 5: Izvršavanje Audita
- Auditori izvršavaju audit
- Beleže se nalazi
- Status se menja na "Completed"

#### Faza 6: Završetak Ciklusa
- Nakon završetka svih audita
- Generiše se izveštaj
- Ciklus se zatvara

### C.3 Integrisan Sistem (Integrated Audit)

**Šta je Integrisan Sistem?**

Kada kompanija ima više od jednog standarda (npr. ISO 9001 + ISO 14001), mogu se auditirati simultano od strane istih auditora u jednom auditnom procesu.

**Prednosti:**
- Brže
- Jeftinije
- Manje smetnji za kompaniju
- Otkriva interakcije između sistema

**Kako se Kreira:**

1. Pri kreiranju ciklusa, unesu se dva ili više standarda
2. Sistem označava kao "Integrated Audit"
3. Broj dana je manji nego suma pojedinačnih standarda
4. Isti auditori se koriste za sve standarde

**Primer:**
- ISO 9001 + ISO 14001 = Integrated Audit
- Trajanje: Obično 3 dana umesto 4-5 dana
- Broj auditora: Može biti ista osoba

---

## D. KALENDAR - NAPREDNE FUNKCIONALNOSTI

### D.1 Prikazi Kalendara

#### Mesečni Prikaz
- Prikazuje cijeli mesec
- Vidljivi su svi eventi u mesecu
- Mogućnost premještanja drag-and-drop

#### Nedeljni Prikaz
- Detaljniji pregled za nedelju
- Vidljivo je vrijeme događaja

#### Dnevni Prikaz
- Detaljniji prikaz za jedan dan
- Vidljiva je tačna vrijednost vremena

### D.2 Drag-and-Drop Premještanje

**Kako Funkcionira:**

1. Kliknite i držite na događaj
2. Povucite na novi datum
3. Otpustite miš
4. Sistem će:
   - Ažurirati datum u bazi
   - Proveriti dostupnost auditora
   - Prikazati potvrdu

**Ograničenja:**

- Možete premještati samo budućie audite
- Završene audite (Completed status) ne možete premještati
- Sistem proverava konflikte auditora
- Prikazuje upozorenje ako je auditor zauzet

### D.3 Dodavanje Novih Audita iz Kalendara

1. Kliknite na slobodan dan
2. Otvorit će se forma za novi audit
3. Popunite:
   - Izaberite ciklus
   - Izaberite vodeći auditor
   - Dodajte dodatne auditory
   - Broj dana
4. Sačuvajte

---

## E. SRBIJA TIM - CRNI KALENDAR (DETALJNO)

### E.1 Šta je Crni Kalendar?

"Crni Kalendar" je specifičan modul za lokalni tim iz Srbije koji vrši:
- Godišnje nadzorne provere
- Održavanje kontakta sa klijentima
- Lokalni auditi
- Poslovanje u domaćem market-u

### E.2 Upravljanje Posjetama

**Dodavanje Nove Posete:**

1. Unesi "Broj sertifikata" - Sistem automatski pronalazi kompaniju
2. Izaberi auditory koji će biti angažovani
3. Izaberi standarde koji će biti auditovani
4. Unesi datum i vreme posete
5. Odaberi status (Zakazan, Odrađen, Otkazan)
6. Optino: Dodaj napomene

**Statusi Poseta:**

- **Zakazan** - Zakazana je, ali još nije odrađena
- **Odrađena** - Poseta je izvršena
- **Otkazana** - Poseta je otkazana
- **Na čekanju** - Čeka se potvrda od kompanije

### E.3 Izveštaji iz Poseta

**Dokumento Izveštaja:**

Nakon što se poseta odradi:
1. Sistem generiše izveštaj
2. Izveštaj se prosljeđuje kompaniji
3. Čeka se povratna informacija
4. Označava se "Izveštaj poslat"

**Praćenje Stanja:**

Na dashboard-u se vide:
- Broj poslanih izveštaja
- Broj neposlanih izveštaja
- Rok za slanje

### E.4 Raspored Auditora Srbija Tim-a

Prikazuje:
- Koji auditor ide gde
- Kada je zakazan
- Koliko je dana slobodno
- Kapacitet za nove audite

**Napomene za Planiranje:**

- Trebate paziti na dostupnost auditora
- Neki auditori mogu imati više od jedne posete dnevno
- Trebate računati putno vreme između lokacija

---

## F. LOKACIJE - DETALJNO

### F.1 Glavni Lokacija vs Dodatne Lokacije

**Glavna Lokacija:**
- Gde je smeštena administracija
- Gde će se održati inicijalni audit
- Obavezna za sve kompanije

**Dodatne Lokacije:**
- Proizvodne hale
- Skladišta
- Distributivni centri
- Kancelarije/filijale
- Mogu biti a ne moraju biti uključene u scope

### F.2 Uključivanje Lokacija u Audit

**Kako se Uključuje Lokacija u Audit:**

1. Pri planiranju audita, auditor bira koje lokacije će biti auditovane
2. Dodeljuje se vreme za svaku lokaciju
3. Auditor putuje između lokacija
4. Izveštaj pokriva sve lokacije

**Primer:**
- Inicijalni audit: Sveže lokacije (3+2 dana)
- Surveillance audit: Samo glavna lokacija (1 dan)
- Recertification: Sve lokacije (3+2 dana)

---

## G. KONTAKT OSOBE - UPRAVLJANJE

### G.1 Primarna vs. Sekundarna Kontakt Osoba

**Primarna Kontakt Osoba:**
- Označena sa zvezdikom (*)
- Prva osoba za kontakt
- Koristi se u svakom događaju
- Obavezna (mora biti najmanje jedna)

**Sekundarne Kontakt Osobe:**
- Osobe sa specifičnim odgovornostima
- Kontaktuju se po potrebi
- Mogu biti Manager Kvalitete, Sigurnosti, itd.

### G.2 Pregled Kontakt Osoba

Na stranici kompanije u tab-u "Kontakti":
- Tabela sa svim osoba
- Njihove pozicije i kontakt podaci
- Oznaka ko je primarna osoba
- Mogućnost izmene i brisanja

### G.3 Tipične Pozicije Kontakt Osoba

| Pozicija | Odgovornost |
|----------|-------------|
| **Direktor** | Opšta odgovornost i donošenje odluka |
| **Manager Kvalitete** | Sistem upravljanja kvalitetom |
| **Manager Okoline** | Zaštita okoline |
| **Manager Sigurnosti** | Sigurnost i zdravlje na radu |
| **Tehnički Direktor** | Tehnički aspekti |
| **Predstavnik Uprave** | Predstavnik u sistemu |
| **Interni Auditor** | Sprovođenje internih audita |

---

## H. IAF/EAC KODOVI - DETALJAN PREGLED

### H.1 Struktura IAF/EAC Kodova

**Format:**
- A01 (glavna kategorija)
- A01.01 (podkategorija)
- A01.01 (dalja potkategorija)

**Primeri:**

**A - Management Systems:**
- A01 - All activities
- A01.01 - Design, development and engineering
- A01.02 - Production and delivery of goods/services
- A01.03 - Distribution of goods/supply of services

**B - Test and Calibration Laboratories:**
- B - Test and calibration laboratories
- B01 - Chemical testing and calibration

**C - Inspection Bodies:**
- C - Inspection bodies
- C01 - Construction and Civil Engineering

### H.2 Primena IAF/EAC Kodova

**Za Kompanije:**
- Specifičan kod se dodeljuje
- Definiše preciznu oblast primene
- Ograničava dozvoljene aktivnosti

**Za Auditory:**
- Auditor mora biti kvalifikovan za kod
- Samo auditore sa kodom mogu auditirati tu domenu
- Sistem automatski filtrira dostupne auditory

### H.3 Primarni Kod

**Koncept Primarnog Koda:**
- Kod koji je suština poslovanju
- Obično je samo jedan
- Označava se sa žutom bojom
- Ostali kodovi su sekundarni

**Primer:**
- Kompanija "Fabrika Kola" - Primarni kod: A01.02 (Proizvodnja)
- Sekundarni kodovi: A01.01 (Dizajn), A01.03 (Distribucija)

---

## I. NAPREDNE OPCIJE I TRIKOVI

### I.1 Masovne Operacije

**Dodavanje više stavki odjednom:**

1. U tabelama sa "+" dugmetom, često možete dodati više stavki
2. Popunite prve podatke
3. Kliknite "Dodaj još jedan"
4. Ponavljajte dok ne završite

### I.2 Brzo Premještanje između Tabova

**Tastaturske Prečice:**

- `Tab` - Premještanje do sledećeg polja
- `Shift + Tab` - Premještanje na prethodno polje
- `Enter` - Potvrda forme (samo ako je dugme fokusirano)

### I.3 Brzo Pretraživanje

**Select2 Dropdowns:**

1. Kliknite na dropdown polje
2. Počnite pisati
3. Список će biti filtriran
4. Pritisnite `Enter` za izbor

**Primer:** Tražite auditor "Marko"
- Kliknite dropdown "Vodeći Auditor"
- Napišite "Marko"
- Biće filtriran na sve Marke
- Izaberite željenog

### I.4 Eksport Podataka

Gde god da vidite " dugme za eksport:
- **Excel** - Za dalje obrade u Excelu
- **PDF** - Za ispis ili arhiviranje
- **CSV** - Za import u druge sisteme

### I.5 Čuvanje Vrati Akcije (Undo)

**Nije dostupno automatski**, ali:
- Proverite "Recent Changes" ako je dostupno
- Kontaktirajte administratora za vraćanje podataka
- Sistme čuva istoriju važnih izmena

---

## J. SIGURNOST I PRIVATNOST

### J.1 Kontrola Pristupa

**Nivoi Pristupa:**
- **Admin** - Pristup svemu
- **Manager** - Может менаџирати аудите и компаније
- **Auditor** - Može pristupiti samo svojim auditima
- **View Only** - Može samo da gleda

### J.2 Lozinka i Sigurnost

**Praksa:**
- Nikad ne delite lozinku
- Koristite jaku lozinku (8+ znakova, brojeve, znakove)
- Odjavljujte se nakon rada
- Proverite "Zapamti me" samo na privatnim računarima

### J.3 Odjava

1. Kliknite na korisničko ime u gornjem desnom uglu
2. Kliknite "Odjava"
3. Bićete prebačeni na stranicu prijave
4. Vaša sesija je završena

---

## K. ČEST PITANJA (FAQ)

### Pitanje: Kako da dodam novu kompaniju?

**Odgovor:**
1. Idite na "Kompanije"
2. Kliknite "+ Nova Kompanija"
3. Popunite obavezna polja
4. Dodajte standarde
5. Kliknite "Sačuvaj"

### Pitanje: Kako da dodam auditora na audit?

**Odgovor:**
1. Otvorite audit
2. U polju "Vodeći auditor", izaberite auditora
3. Dodajte dodatne auditory ako trebate
4. Система će proveriti dostupnost
5. Kliknite "Sačuvaj"

### Pitanje: Kako da odložim audit?

**Odgovor:**
1. Otvorite audit
2. Promenite "Status" na "Postponed"
3. Opciono: Unesite novi datum
4. Kliknite "Sačuvaj"

### Pitanje: Šta da uradim ako ne vidim kompaniju u listi?

**Odgovor:**
1. Koristite pretragu sa ključnim rečima
2. Proverite filter po statusu
3. Ako i dalje ne vidite, kompanija možda nije kreirana
4. Kreirajte je koristeći "+ Nova Kompanija"

### Pitanje: Kako se računa istek sertifikata?

**Odgovor:**
- Sertifikat je validan 3 godine od datuma izdavanja
- Sistem automatski dodaje 3 godine
- Na dashboard-u se prikazuje broj dana do isteka
- Ako ostane manje od 30 dana, prikazuje se crveno

### Pitanje: Šta su IAF/EAC kodovi?

**Odgovor:**
- Kodovi koji označavaju specifičnu oblast primene
- Svaki standard ima svoje kodove
- Auditor mora biti kvalifikovan za kod
- Kompanija mora imati odgovarajući kod

---

## L. PROBLEM SOLVING GUIDE

### Problem: "Greška pri čuvanju: Obavezna polja"

**Koraci za Rešavanje:**
1. Kliknite na dugme "+" pri korišćenju formi
2. Sistem će prikazati koja polja su obavezna
3. Popunite sve obavezne (označene sa *)
4. Pokušajte ponovo

### Problem: "Auditor se ne može dodeliti"

**Mogućih Razloga:**
1. Auditor nema potrebni standard
   - Rešenje: Dodajte standard auditori
2. Auditor je zauzet taj dan
   - Rešenje: Odaberite drugi auditor
3. Auditor nema potrebni IAF/EAC kod
   - Rešenje: Dodajte kod auditori

### Problem: "Pretraga ne pronalazi kompaniju"

**Koraci za Rešavanje:**
1. Proverite da ste napisali ispravno (velika/mala slova?)
2. Pokušajte samo sa delom imena
3. Resetujte filter
4. Proverite status filtera

### Problem: "Calendar se ne učitava"

**Koraci za Rešavanje:**
1. Osvežite stranicu (F5)
2. Obrisanje cache (Ctrl+Shift+Del)
3. Pokušajte u drugom browser-u
4. Kontaktirajte IT podrške

---

**Verzija:** 2.0
**Zadnje Ažuriranje:** 2025-01-15

