# Dashboard - Predlog Strukture i Metrika

## 📊 Pregled Ključnih Metrika (KPI Cards)

### 1. **Kompanije - Statistika**
- **Ukupan broj kompanija**: Prikaz ukupnog broja registrovanih kompanija
- **Aktivni sertifikati**: Broj kompanija sa statusom `active`
- **Suspendovani**: Broj kompanija sa statusom `suspended`
- **Istekli**: Broj kompanija sa statusom `expired`
- **Na čekanju**: Broj kompanija sa statusom `pending`

**Boje kartice:**
- Aktivni: Zelena (#28a745)
- Suspendovani: Žuta (#ffc107)
- Istekli: Crvena (#dc3545)
- Na čekanju: Plava (#007bff)

---

### 2. **Auditi - Pregled Statusa**
- **Planirani auditi**: Broj audita sa statusom `planned`
- **Zakazani auditi**: Broj audita sa statusom `scheduled`
- **Završeni auditi (ovaj mesec)**: Broj audita završenih u tekućem mesecu
- **Odloženi auditi**: Broj audita sa statusom `postponed`

**Dodatno:**
- **Auditi u narednih 30 dana**: Lista audita koji su planirani u narednih 30 dana
- **Prosečan broj dana po auditu**: Izračunato na osnovu `audit_days` iz ciklusa

---

### 3. **Srbija Tim - Crni Kalendar**
- **Zakazane posete (ovaj mesec)**: Broj poseta sa statusom `zakazan`
- **Odrađene posete (ovaj mesec)**: Broj poseta sa statusom `odradjena`
- **Poslati izveštaji**: Broj poseta gde je `report_sent = True`
- **Neposlati izveštaji**: Broj odrađenih poseta gde je `report_sent = False`

**Dodatno:**
- **Posete u narednih 7 dana**: Lista predstojećih poseta

---

### 4. **Sertifikati - Isticanje**
- **Sertifikati koji ističu u narednih 30 dana**: Broj kompanija čiji sertifikati ističu uskoro
- **Sertifikati koji ističu u narednih 60 dana**: Broj kompanija
- **Sertifikati koji ističu u narednih 90 dana**: Broj kompanija
- **Već istekli sertifikati**: Broj kompanija sa isteklim sertifikatima

**Vizualizacija:**
- Grafikon (bar chart) sa distribucijom po mesecima

---

### 5. **Auditori - Zauzetost**
- **Ukupan broj auditora**: Broj registrovanih auditora
- **Najzauzetiji auditor (ovaj mesec)**: Auditor sa najviše rezervacija
- **Dostupni auditori (danas)**: Broj auditora bez rezervacija za današnji dan
- **Auditori sa najviše završenih audita (ova godina)**: Top 3 auditora

---

### 6. **Ciklusi Sertifikacije**
- **Aktivni ciklusi**: Broj ciklusa sa statusom `active`
- **Završeni ciklusi (ova godina)**: Broj ciklusa završenih u tekućoj godini
- **Integrisani sistemi**: Broj ciklusa gde je `is_integrated_system = True`
- **Prosečno trajanje ciklusa**: Izračunato na osnovu datuma početka i završetka

---

## 📈 Grafikoni i Vizualizacije

### 1. **Auditi po Mesecima (Line Chart)**
- X-osa: Meseci (poslednih 12 meseci)
- Y-osa: Broj audita
- Linije:
  - Planirani auditi
  - Završeni auditi
  - Odloženi auditi

### 2. **Distribucija Kompanija po Statusu (Pie Chart)**
- Segmenti:
  - Aktivni
  - Suspendovani
  - Istekli
  - Na čekanju
  - Otkazani

### 3. **Distribucija po Industrijama (Bar Chart)**
- X-osa: Industrije (iz `INDUSTRY_CHOICES`)
- Y-osa: Broj kompanija

### 4. **Srbija Tim - Status Poseta (Donut Chart)**
- Segmenti:
  - Zakazane
  - Nije zakazano
  - Odrađene posete
  - Poslati izveštaji

### 5. **Auditori - Zauzetost (Horizontal Bar Chart)**
- X-osa: Broj rezervacija
- Y-osa: Imena auditora (Top 10)

---

## 📋 Tabele sa Ključnim Podacima

### 1. **Predstojeći Auditi (Narednih 14 Dana)**
| Kompanija | Tip Audita | Planirani Datum | Vodeći Auditor | Status |
|-----------|------------|-----------------|----------------|--------|
| ...       | ...        | ...             | ...            | ...    |

**Akcije:**
- Link ka detaljima audita
- Dugme "Izmeni"
- Dugme "Zakaži"

---

### 2. **Sertifikati koji Ističu (Narednih 30 Dana)**
| Kompanija | Broj Sertifikata | Datum Isticanja | Broj Dana | Akcija |
|-----------|------------------|-----------------|-----------|--------|
| ...       | ...              | ...             | ...       | ...    |

**Boje:**
- Crvena: Manje od 7 dana
- Žuta: 7-30 dana
- Zelena: Više od 30 dana

---

### 3. **Najnovije Aktivnosti (Activity Feed)**
- **Poslednje kreirane kompanije** (5 najnovijih)
- **Poslednje završeni auditi** (5 najnovijih)
- **Poslednje dodate posete (Srbija Tim)** (5 najnovijih)
- **Poslednje izmene ciklusa** (5 najnovijih)

Format:
```
[Ikona] [Tip aktivnosti] - [Naziv] - [Datum/Vreme]
```

---

### 4. **Neposlati Izveštaji (Srbija Tim)**
| Kompanija | Broj Sertifikata | Datum Posete | Auditori | Akcija |
|-----------|------------------|--------------|----------|--------|
| ...       | ...              | ...          | ...      | ...    |

**Filter:**
- Samo odrađene posete gde je `report_sent = False`

---

## 🔔 Upozorenja i Notifikacije

### 1. **Kritična Upozorenja (Alerts)**
- **Istekli sertifikati**: Broj kompanija sa isteklim sertifikatima
- **Odloženi auditi**: Broj audita koji su odloženi više od 30 dana
- **Neposlati izveštaji**: Broj odrađenih poseta bez poslatog izveštaja (stariji od 7 dana)

**Vizualizacija:**
- Crveni badge sa brojem
- Klik otvara listu sa detaljima

### 2. **Informativna Upozorenja (Info)**
- **Auditi bez dodeljenog auditora**: Broj zakazanih audita bez vodećeg auditora
- **Kompanije bez kontakt osobe**: Broj kompanija bez primarne kontakt osobe
- **Ciklusi bez standarda**: Broj ciklusa bez dodeljenih standarda

---

## 🎨 Layout Predlog

```
+----------------------------------------------------------+
|  [Logo]  Dashboard                          [User Menu]  |
+----------------------------------------------------------+
|                                                          |
|  +-------------+  +-------------+  +-------------+       |
|  | Kompanije   |  | Auditi      |  | Srbija Tim  |       |
|  | 150 Aktivni |  | 25 Planirani|  | 12 Zakazano |       |
|  +-------------+  +-------------+  +-------------+       |
|                                                          |
|  +-------------+  +-------------+  +-------------+       |
|  | Sertifikati |  | Auditori    |  | Ciklusi     |       |
|  | 8 Ističu    |  | 15 Aktivnih |  | 45 Aktivnih |       |
|  +-------------+  +-------------+  +-------------+       |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  +------------------------+  +-------------------------+ |
|  | Auditi po Mesecima     |  | Distribucija Kompanija | |
|  | [Line Chart]           |  | [Pie Chart]            | |
|  +------------------------+  +-------------------------+ |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  +--------------------------------------------------+   |
|  | Predstojeći Auditi (Narednih 14 Dana)            |   |
|  | [Tabela sa podacima]                             |   |
|  +--------------------------------------------------+   |
|                                                          |
|  +--------------------------------------------------+   |
|  | Sertifikati koji Ističu (Narednih 30 Dana)       |   |
|  | [Tabela sa podacima]                             |   |
|  +--------------------------------------------------+   |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  +------------------------+  +-------------------------+ |
|  | Najnovije Aktivnosti   |  | Upozorenja              | |
|  | [Activity Feed]        |  | [Alert List]            | |
|  +------------------------+  +-------------------------+ |
|                                                          |
+----------------------------------------------------------+
```

---

## 🛠️ Tehnička Implementacija

### Backend (Django View)
```python
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Kompanije statistika
        context['total_companies'] = Company.objects.count()
        context['active_companies'] = Company.objects.filter(certificate_status='active').count()
        context['suspended_companies'] = Company.objects.filter(certificate_status='suspended').count()
        context['expired_companies'] = Company.objects.filter(certificate_status='expired').count()
        
        # Auditi statistika
        context['planned_audits'] = CycleAudit.objects.filter(audit_status='planned').count()
        context['scheduled_audits'] = CycleAudit.objects.filter(audit_status='scheduled').count()
        context['upcoming_audits'] = CycleAudit.objects.filter(
            planned_date__gte=today,
            planned_date__lte=today + timedelta(days=30)
        ).order_by('planned_date')[:10]
        
        # Srbija Tim statistika
        context['srbija_tim_scheduled'] = SrbijaTim.objects.filter(
            status='zakazan',
            visit_date__month=today.month
        ).count()
        context['srbija_tim_completed'] = SrbijaTim.objects.filter(
            status='odradjena',
            visit_date__month=today.month
        ).count()
        context['reports_sent'] = SrbijaTim.objects.filter(report_sent=True).count()
        context['reports_pending'] = SrbijaTim.objects.filter(
            status='odradjena',
            report_sent=False
        ).count()
        
        # Sertifikati koji ističu
        context['expiring_30_days'] = Company.objects.filter(
            certificate_expiry_date__gte=today,
            certificate_expiry_date__lte=today + timedelta(days=30)
        ).count()
        
        # Auditori
        context['total_auditors'] = Auditor.objects.count()
        
        # Ciklusi
        context['active_cycles'] = CertificationCycle.objects.filter(status='active').count()
        context['integrated_systems'] = CertificationCycle.objects.filter(is_integrated_system=True).count()
        
        return context
```

### Frontend (Chart.js za grafikone)
- **Line Chart**: Auditi po mesecima
- **Pie Chart**: Distribucija kompanija po statusu
- **Bar Chart**: Distribucija po industrijama
- **Donut Chart**: Srbija Tim status poseta

---

## 📱 Responsive Design
- **Desktop**: 3 kolone za KPI kartice
- **Tablet**: 2 kolone
- **Mobile**: 1 kolona

---

## 🔄 Refresh Interval
- **Auto-refresh**: Svaka 5 minuta (opciono)
- **Manual refresh**: Dugme "Osveži podatke"

---

## 🎯 Prioritet Implementacije

### Faza 1 (Osnovne Metrike)
1. KPI kartice (Kompanije, Auditi, Srbija Tim)
2. Tabela predstojećih audita
3. Tabela sertifikata koji ističu

### Faza 2 (Vizualizacije)
4. Line chart - Auditi po mesecima
5. Pie chart - Distribucija kompanija
6. Activity feed

### Faza 3 (Napredne Funkcije)
7. Upozorenja i notifikacije
8. Dodatni grafikoni
9. Export funkcionalnost (PDF/Excel)

---

## 📝 Napomene
- Svi podaci se učitavaju dinamički iz baze
- Koristiti Django ORM agregacije za optimizaciju
- Implementirati caching za bolje performanse
- Dodati permisije za različite nivoe pristupa
