from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
import math


def zaokruzi_na_veci_broj(vrednost):
    """
    Zaokružuje decimalnu vrednost na veći ceo broj ako ima decimalni deo .5 ili veći.
    Ako je vrednost None ili 0, vraća 0.
    """
    if vrednost is None or vrednost == 0:
        return 0
    
    # Konvertujemo u float za svaki slučaj
    vrednost_float = float(vrednost)
    
    # Zaokružujemo na veći ceo broj ako je decimalni deo .5 ili veći
    return math.ceil(vrednost_float)

from .company_models import Company
from .standard_models import StandardDefinition, CompanyStandard
from .auditor_models import Auditor


class CertificationCycle(models.Model):
    """
    Model za praćenje ciklusa sertifikacije koji uključuje inicijalnu sertifikaciju,
    nadzorne provere i resertifikaciju.
    """
    CYCLE_STATUS_CHOICES = [
        ('active', _('Aktivan')),
        ('completed', _('Završen')),
        ('cancelled', _('Otkazan')),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='certification_cycles',
        verbose_name=_('Kompanija')
    )
    
    # Da li je integrisani sistem menadžmenta
    is_integrated_system = models.BooleanField(
        _('Integrisani sistem menadžmenta'), 
        default=False,
        help_text=_('Označiti ako je u pitanju integrisani sistem koji obuhvata ISO 9001, 14001 i/ili 45001 standard')
    )
    
    # Datum početka ciklusa sertifikacije (datum inicijalne sertifikacije)
    # Fizička kolona u bazi: 'planirani_datum' (preimenovana sa 'start_date' kroz migraciju 0033)
    planirani_datum = models.DateField(_('Planirani datum ciklusa'), help_text=_('Datum inicijalne sertifikacije'))
    
    datum_sprovodjenja_inicijalne = models.DateField(_('Datum sprovođenja inicijalne'), null=True, blank=True, help_text=_('Datum kada je sprovedena inicijalna provera'))
    
    status = models.CharField(_('Status ciklusa'), max_length=20, choices=CYCLE_STATUS_CHOICES, default='active')

    # Polja za planirani broj dana audita
    inicijalni_broj_dana = models.DecimalField(
        _('Planirani inicijalni dani'), 
        max_digits=5, 
        decimal_places=1, 
        blank=True, 
        null=True,
        help_text=_('Planirani broj dana za inicijalni audit')
    )
    broj_dana_nadzora = models.DecimalField(
        _('Planirani dani nadzora'), 
        max_digits=5, 
        decimal_places=1, 
        blank=True, 
        null=True,
        help_text=_('Planirani broj dana za nadzorni audit')
    )
    broj_dana_resertifikacije = models.DecimalField(
        _('Planirani dani resertifikacije'), 
        max_digits=5, 
        decimal_places=1, 
        blank=True, 
        null=True,
        help_text=_('Planirani broj dana za resertifikacioni audit')
    )
    
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    class Meta:
        verbose_name = _('Ciklus sertifikacije')
        verbose_name_plural = _('Ciklusi sertifikacije')
        ordering = ['-planirani_datum']
    
    def __str__(self):
        return f"{self.company.name} - {self.planirani_datum.strftime('%Y-%m-%d')} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Detektujemo prethodnu vrednost stvarnog datuma inicijalne provere
        prev_actual_date = None
        if self.pk:
            try:
                prev_actual_date = CertificationCycle.objects.get(pk=self.pk).datum_sprovodjenja_inicijalne
            except CertificationCycle.DoesNotExist:
                prev_actual_date = None

        super().save(*args, **kwargs)
        # Nakon snimanja proverimo i ažuriramo status integrisanog sistema
        self.detect_integrated_system()

        # Ako je unet ili promenjen stvarni datum inicijalne provere, zakaži prvi nadzor
        if self.datum_sprovodjenja_inicijalne and self.datum_sprovodjenja_inicijalne != prev_actual_date:
            self.ensure_first_surveillance_scheduled()
    
    def detect_integrated_system(self):
        """
        Detektuje da li je u pitanju integrisani sistem menadžmenta na osnovu 
        standarda koji su uključeni u ciklus.
        """
        # Lista kodova standarda koji čine integrisani sistem
        integrated_standards = ['9001', '14001', '45001']
        
        if not hasattr(self, 'cycle_standards'):
            return False
            
        # Standardi koji su uključeni u ciklus
        cycle_standards = self.cycle_standards.values_list('standard_definition__code', flat=True)
        
        # Brojanje standarda integrisanog sistema
        integrated_count = sum(1 for std in cycle_standards if any(istd in std for istd in integrated_standards))
        
        # Ako imamo dva ili više standarda integrisanog sistema, označavamo kao integrisani
        if integrated_count >= 2:
            if not self.is_integrated_system:
                self.is_integrated_system = True
                self.save(update_fields=['is_integrated_system'])
            return True
        return False
    
    def create_default_audits(self, is_first_cycle=False):
        """
        Automatski kreira inicijalni audit i (kada je dostupan stvarni datum inicijalne provere)
        prvi nadzorni audit za ciklus sertifikacije.
        Za prvi ciklus kreira samo inicijalni audit kao planiran; prvi nadzor se zakazuje tek
        nakon unosa stvarnog datuma inicijalne provere.
        """
        from datetime import timedelta
        
        # Samo za prvi ciklus kreiramo inicijalni audit
        if is_first_cycle:
            # Inicijalni audit (planiran na datum početka ciklusa)
            initial_audit, created = CycleAudit.objects.get_or_create(
                certification_cycle=self,
                audit_type='initial',
                defaults={
                    'planned_date': self.planirani_datum,
                    'audit_status': 'planned'
                }
            )
            # Kreiraj dane audita da bi se prikazao u kalendaru
            if created or not initial_audit.audit_days.exists():
                initial_audit.create_audit_days()
            
            # Ako je već unet stvarni datum, odmah zakazujemo prvi nadzor
            if self.datum_sprovodjenja_inicijalne:
                self.ensure_first_surveillance_scheduled()

    def ensure_first_surveillance_scheduled(self):
        """Zakazuje ili ažurira prvi nadzorni audit na osnovu stvarnog datuma inicijalne provere."""
        from datetime import timedelta
        if not self.datum_sprovodjenja_inicijalne:
            return
        
        # Izračunavanje datuma prvog nadzora
        if self.broj_dana_nadzora:
            broj_dana = zaokruzi_na_veci_broj(self.broj_dana_nadzora)
            first_surveillance_date = self.datum_sprovodjenja_inicijalne + timedelta(days=365) - timedelta(days=broj_dana)
        else:
            # Fallback: godinu dana nakon stvarnog datuma inicijalne provere
            first_surveillance_date = self.datum_sprovodjenja_inicijalne + timedelta(days=365)

        audit, created = CycleAudit.objects.get_or_create(
            certification_cycle=self,
            audit_type='surveillance_1',
            defaults={
                'planned_date': first_surveillance_date,
                'audit_status': 'planned'
            }
        )
        if not created and audit.planned_date != first_surveillance_date:
            audit.planned_date = first_surveillance_date
            audit.save(update_fields=['planned_date'])
    
    def extend_with_new_audits(self, recertification_audit=None):
        """
        Označava trenutni ciklus sertifikacije kao završen i kreira novi ciklus nakon što je završen resertifikacioni audit.
        """
        from datetime import timedelta
        import logging
        logger = logging.getLogger('django')
        logger.info(f"Pozivam extend_with_new_audits za ciklus {self.id} sa resertifikacionim auditom {recertification_audit.id if recertification_audit else None}")
        
        # Ako je završen resertifikacioni audit, kreiramo novi ciklus
        if recertification_audit and recertification_audit.actual_date:
            new_start_date = recertification_audit.actual_date
        else:
            # Ako nema stvarnog datuma, koristimo planirani datum ili projekciju kraja ciklusa (3 godine od početka)
            if recertification_audit and recertification_audit.planned_date:
                new_start_date = recertification_audit.planned_date
            else:
                new_start_date = self.planirani_datum + timedelta(days=3*365)
        
        logger.info(f"Novi početni datum: {new_start_date}")
        
        # Označavamo trenutni ciklus kao završen
        self.status = 'completed'
        self.notes = f"{self.notes or ''}\nCiklus završen nakon resertifikacije {new_start_date.strftime('%Y-%m-%d')}."
        
        # Sačuvamo promene u trenutnom ciklusu
        self.save(update_fields=['status', 'notes'])
        logger.info(f"Ciklus {self.id} označen kao završen")
        
        # Ako već postoji ciklus sa istim početnim datumom za istu kompaniju, koristimo njega (idempotentnost)
        new_cycle = CertificationCycle.objects.filter(company=self.company, planirani_datum=new_start_date).first()
        if new_cycle:
            logger.info(f"Pronađen postojeći ciklus {new_cycle.id} sa istim početnim datumom {new_start_date}, preskačem kreiranje.")
        else:
            # Kreiramo novi ciklus sertifikacije
            new_cycle = CertificationCycle.objects.create(
                company=self.company,
                is_integrated_system=self.is_integrated_system,
                planirani_datum=new_start_date,
                status='active',
                inicijalni_broj_dana=self.inicijalni_broj_dana,
                broj_dana_nadzora=self.broj_dana_nadzora,
                broj_dana_resertifikacije=self.broj_dana_resertifikacije,
                notes=f"Novi ciklus kreiran nakon završetka prethodnog ciklusa. Početak: {new_start_date.strftime('%Y-%m-%d')}"
            )
        logger.info(f"Kreiran novi ciklus {new_cycle.id} sa početkom {new_start_date}")
        
        # Kopiramo standarde iz starog ciklusa u novi (idempotentno)
        for cycle_standard in self.cycle_standards.all():
            CycleStandard.objects.get_or_create(
                certification_cycle=new_cycle,
                standard_definition=cycle_standard.standard_definition,
                defaults={
                    'company_standard': cycle_standard.company_standard,
                    'notes': cycle_standard.notes,
                }
            )
        logger.info(f"Kopirani standardi iz ciklusa {self.id} u novi ciklus {new_cycle.id}")
        
        # U novom ciklusu ne kreiramo inicijalni audit, samo prvi nadzorni audit
        logger.info(f"Preskačemo kreiranje inicijalnog audita za novi ciklus {new_cycle.id}")
        
        # Kreiramo prvi nadzorni audit za novi ciklus
        # Prvi nadzor = Datum sprovođenja inicijalne provere + 1 godina - Broj dana nadzora
        if new_cycle.broj_dana_nadzora:
            # Zaokružujemo broj_dana_nadzora na veći ceo broj ako ima decimalni deo .5 ili veći
            broj_dana = zaokruzi_na_veci_broj(new_cycle.broj_dana_nadzora)
            first_surveillance_date = new_start_date + timedelta(days=365) - timedelta(days=broj_dana)
        else:
            # Ako nemamo potrebne podatke, koristimo standardnu formulu (godinu dana nakon inicijalne)
            first_surveillance_date = new_start_date + timedelta(days=365)
        
        # Kreiramo prvi nadzorni audit za novi ciklus (idempotentno)
        s1_audit, s1_created = CycleAudit.objects.get_or_create(
            certification_cycle=new_cycle,
            audit_type='surveillance_1',
            defaults={
                'planned_date': first_surveillance_date,
                'audit_status': 'planned'
            }
        )
        if not s1_created and s1_audit.planned_date != first_surveillance_date:
            s1_audit.planned_date = first_surveillance_date
            s1_audit.save(update_fields=['planned_date'])
        logger.info(f"Prvi nadzorni audit za novi ciklus {new_cycle.id}: ID={s1_audit.id}, planirani datum={s1_audit.planned_date}")
        
        return new_cycle
        
    def create_next_certification_cycle(self, recertification_audit=None):
        """
        Kreira novi ciklus sertifikacije nakon što je završen resertifikacioni audit.
        Kopira relevantne podatke iz tekućeg ciklusa i postavlja nove datume.
        
        Napomena: Ova metoda je zadržana zbog kompatibilnosti, ali se više ne koristi.
        Umesto nje se sada koristi extend_with_new_audits.
        """
        # Ova metoda je zadržana samo zbog kompatibilnosti sa starim kodom
        # Sada se umesto nje koristi extend_with_new_audits
        return None

    def get_last_planned_audit_date(self):
        """
        Vraća poslednji planirani datum audita u ovom ciklusu.
        Gleda sve audite u ciklusu i vraća najkasniji planned_date.
        """
        from django.db.models import Max
        
        last_audit = self.audits.aggregate(Max('planned_date'))
        return last_audit['planned_date__max']
    
    def get_next_planned_audit_date(self):
        """
        Vraća sledeći planirani datum audita (u budućnosti).
        """
        from datetime import date
        today = date.today()
        
        next_audit = self.audits.filter(
            planned_date__gte=today,
            audit_status__in=['planned', 'scheduled']
        ).order_by('planned_date').first()
        
        return next_audit.planned_date if next_audit else None
    
    def get_latest_audit_info(self):
        """
        Vraća informacije o poslednjem planiranom auditu.
        Ako postoji budući audit, vraća njega, inače poslednji.
        """
        from datetime import date
        today = date.today()
        
        # Prvo pokušaj da nađeš budući audit
        future_audit = self.audits.filter(
            planned_date__gte=today,
            audit_status__in=['planned', 'scheduled']
        ).order_by('planned_date').first()
        
        if future_audit:
            return {
                'date': future_audit.planned_date,
                'type': future_audit.get_audit_type_display(),
                'status': future_audit.get_audit_status_display(),
                'is_future': True
            }
        
        # Ako nema budućih, vrati poslednji planirani
        last_audit = self.audits.order_by('-planned_date').first()
        
        if last_audit:
            return {
                'date': last_audit.planned_date,
                'type': last_audit.get_audit_type_display(),
                'status': last_audit.get_audit_status_display(),
                'is_future': False
            }
        
        return None
    
class CycleStandard(models.Model):
    """Model koji povezuje ciklus sertifikacije sa standardima koji su uključeni u taj ciklus."""
    certification_cycle = models.ForeignKey(
        CertificationCycle,
        on_delete=models.CASCADE,
        related_name='cycle_standards',
        verbose_name=_('Ciklus sertifikacije')
    )
    
    standard_definition = models.ForeignKey(
        StandardDefinition,
        on_delete=models.CASCADE,
        related_name='certification_cycles',
        verbose_name=_('Standard')
    )
    
    company_standard = models.ForeignKey(
        CompanyStandard,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='certification_cycles',
        verbose_name=_('Standard kompanije')
    )
    
    # Opciono: dodatni podaci specifični za standard u ciklusu
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    class Meta:
        verbose_name = _('Standard u ciklusu')
        verbose_name_plural = _('Standardi u ciklusu')
        unique_together = [['certification_cycle', 'standard_definition']]
        
    def __str__(self):
        return f"{self.certification_cycle.company.name} - {self.standard_definition.code} ({self.certification_cycle.planirani_datum.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nakon dodavanja standarda, proverimo da li je integrisani sistem
        self.certification_cycle.detect_integrated_system()


class AuditDay(models.Model):
    """Model za praćenje pojedinačnih dana audita."""
    audit = models.ForeignKey(
        'CycleAudit',  # Koristimo string jer je CycleAudit definisan kasnije
        on_delete=models.CASCADE,
        related_name='audit_days',
        verbose_name=_('Audit')
    )

    date = models.DateField(_('Datum'))
    is_planned = models.BooleanField(_('Planirano'), default=True)
    is_actual = models.BooleanField(_('Stvarno'), default=False)
    notes = models.TextField(_('Napomene'), blank=True, null=True)

    class Meta:
        verbose_name = _('Dan audita')
        verbose_name_plural = _('Dani audita')
        ordering = ['date']

    def __str__(self):
        return f"{self.audit} - {self.date.strftime('%Y-%m-%d')}"


class AuditorReservation(models.Model):
    """Rezervacija auditora po datumu kako bi se sprečilo duplo zakazivanje."""
    auditor = models.ForeignKey(
        Auditor,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Auditor')
    )
    date = models.DateField(_('Datum'))
    audit = models.ForeignKey(
        'CycleAudit',
        on_delete=models.CASCADE,
        related_name='auditor_reservations',
        verbose_name=_('Audit')
    )
    audit_day = models.ForeignKey(
        'AuditDay',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Dan audita'),
        null=True,
        blank=True
    )
    role = models.CharField(
        _('Uloga'),
        max_length=10,
        blank=True,
        null=True,
        choices=[('lead', _('Vodeći')), ('team', _('Tim'))]
    )
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)

    class Meta:
        verbose_name = _('Rezervacija auditora')
        verbose_name_plural = _('Rezervacije auditora')
        unique_together = [['auditor', 'date']]
        ordering = ['date']
        indexes = [
            models.Index(fields=['audit', 'date'], name='audres_audit_date_idx'),
        ]

    def __str__(self):
        return f"{self.auditor} - {self.date.strftime('%Y-%m-%d')} ({self.audit})"


class CycleAudit(models.Model):
    """Model za praćenje pojedinačnih audita u okviru ciklusa sertifikacije."""
    AUDIT_TYPE_CHOICES = [
        ('initial', _('Inicijalni')),
        ('surveillance_1', _('Prvi nadzor')),
        ('surveillance_2', _('Drugi nadzor')),
        ('recertification', _('Resertifikacija')),
        ('special', _('Specijalni')),
    ]

    AUDIT_STATUS_CHOICES = [
        ('planned', _('Planirano')),
        ('postponed', _('Odloženo')),
        ('scheduled', _('Zakazano')),
        ('completed', _('Završeno')),
        ('cancelled', _('Otkazano')),
  
    ]

    certification_cycle = models.ForeignKey(
        CertificationCycle,
        on_delete=models.CASCADE,
        related_name='audits',
        verbose_name=_('Ciklus sertifikacije')
    )

    audit_type = models.CharField(_('Tip audita'), max_length=20, choices=AUDIT_TYPE_CHOICES)
    audit_status = models.CharField(_('Status audita'), max_length=20, choices=AUDIT_STATUS_CHOICES, default='planned')
    
    # Polja za datume
    planned_date = models.DateField(_('Planirani datum'))
    actual_date = models.DateField(_('Stvarni datum'), null=True, blank=True)
    
    lead_auditor = models.ForeignKey(
        Auditor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='lead_audits',
        verbose_name=_('Vodeći auditor')
    )
    
    audit_team = models.ManyToManyField(
        Auditor,
        related_name='audit_participations',
        verbose_name=_('Tim auditora'),
        blank=True
    )
    
    report_number = models.CharField(_('Broj izveštaja'), max_length=100, blank=True, null=True)
    findings = models.TextField(_('Nalazi'), blank=True, null=True)
    recommendations = models.TextField(_('Preporuke'), blank=True, null=True)
    poslat_izvestaj = models.BooleanField(_('Poslat izveštaj'), default=False, help_text=_('Označite ako je izveštaj poslat klijentu'))
    
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    # Pratimo prethodne vrednosti za detekciju promena
    _prev_audit_status = None
    _prev_planned_date = None
    _prev_actual_date = None
    
    class Meta:
        verbose_name = _('Audit u ciklusu')
        verbose_name_plural = _('Auditi u ciklusu')
        ordering = ['planned_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pratimo prethodni status audita da bismo znali kada je promenjen
        self._prev_audit_status = self.audit_status if self.pk else None
        # Pratimo prethodni planirani datum da bismo znali kada je promenjen
        self._prev_planned_date = self.planned_date if self.pk else None
        # Pratimo prethodni stvarni datum da bismo mogli reagovati i kada se ukloni/stavi
        self._prev_actual_date = self.actual_date if self.pk else None
    
    def create_audit_days(self):
        """
        Kreira dane audita na osnovu planiranog/stvarnog datuma i broja dana audita.
        Pravilo:
        - Ako postoji stvarni datum (actual_date), brišu se SVI planirani dani i kreiraju se samo stvarni dani.
        - Ako ne postoji stvarni datum, kreiraju se planirani dani unazad od planiranog datuma.
        """
        import logging
        from datetime import timedelta
        logger = logging.getLogger('django')
        
        # Određujemo broj dana audita na osnovu tipa audita
        cycle = self.certification_cycle
        if self.audit_type == 'initial' and cycle.inicijalni_broj_dana:
            broj_dana = zaokruzi_na_veci_broj(cycle.inicijalni_broj_dana)
        elif (self.audit_type == 'surveillance_1' or self.audit_type == 'surveillance_2') and cycle.broj_dana_nadzora:
            broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_nadzora)
        elif self.audit_type == 'recertification' and cycle.broj_dana_resertifikacije:
            broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_resertifikacije)
        else:
            broj_dana = 1  # Podrazumevano 1 dan ako nije definisano
        
        logger.info(f"Priprema dana audita za audit ID={self.pk}, tip={self.audit_type}, planned={self.planned_date}, actual={self.actual_date}")
        
        # Uvek obriši postojeće planirane dane; ne želimo ih kada postoji actual_date
        deleted_planned, _ = self.audit_days.filter(is_planned=True).delete()
        logger.info(f"Obrisano planiranih dana: {deleted_planned}")
        
        audit_days = []
        
        if self.actual_date:
            # Kada postoji stvarni datum, kreiramo SAMO stvarne dane
            deleted_actual, _ = self.audit_days.filter(is_actual=True).delete()
            logger.info(f"Obrisano stvarnih dana (pre re-kreiranja): {deleted_actual}")
            for i in range(broj_dana):
                audit_date = self.actual_date - timedelta(days=i)
                audit_day = AuditDay(
                    audit=self,
                    date=audit_date,
                    is_planned=False,
                    is_actual=True
                )
                audit_days.append(audit_day)
        else:
            # Nema stvarnog datuma -> kreiramo planirane dane od planiranog datuma
            # Takođe, ako su eventualno postojali stvarni dani od ranije, obriši ih
            deleted_actual, _ = self.audit_days.filter(is_actual=True).delete()
            if deleted_actual:
                logger.info(f"Obrisano stvarnih dana (jer actual_date nije postavljen): {deleted_actual}")
            for i in range(broj_dana):
                audit_date = self.planned_date - timedelta(days=i)
                audit_day = AuditDay(
                    audit=self,
                    date=audit_date,
                    is_planned=True,
                    is_actual=False
                )
                audit_days.append(audit_day)
        
        # Čuvamo dane audita
        AuditDay.objects.bulk_create(audit_days)
        logger.info(f"Kreirano novih dana audita: {len(audit_days)}")
    
    def sync_auditor_reservations(self):
        """
        Sinhronizuje rezervacije auditora sa trenutnim danima audita i dodeljenim auditorima
        (vodeći + tim). Ne pravi duplikate i uklanja zastarele rezervacije za ovaj audit.
        """
        from django.db.models import Q
        # Trenutno dodeljeni auditori
        assigned_auditors = list(self.audit_team.all())
        if self.lead_auditor_id:
            assigned_auditors.append(self.lead_auditor)

        # Mapiranje datuma -> AuditDay radi direktnog povezivanja rezervacija sa danima
        day_by_date = {ad.date: ad for ad in self.audit_days.all()}
        dates = list(day_by_date.keys())

        # Ako nema datuma ili nema auditora, obriši sve rezervacije za ovaj audit
        if not dates or not assigned_auditors:
            AuditorReservation.objects.filter(audit=self).delete()
            return

        # Ukloni rezervacije ovog audita koje se više ne odnose na aktuelne datume ili auditore
        AuditorReservation.objects.filter(audit=self).exclude(date__in=dates).delete()
        AuditorReservation.objects.filter(audit=self).exclude(auditor__in=[a.id for a in assigned_auditors]).delete()

        # Kreiraj ili ažuriraj rezervacije i poveži ih sa odgovarajućim AuditDay zapisom
        for auditor in assigned_auditors:
            role = 'lead' if self.lead_auditor_id and auditor.id == self.lead_auditor_id else 'team'
            for d in dates:
                # Ako već postoji rezervacija za istog auditora i datum za DRUGI audit, preskoči (sukob)
                if AuditorReservation.objects.filter(auditor=auditor, date=d).exclude(audit=self).exists():
                    continue
                res, created = AuditorReservation.objects.get_or_create(
                    auditor=auditor,
                    date=d,
                    audit=self,
                    defaults={'role': role, 'audit_day': day_by_date.get(d)}
                )
                # Ažuriraj ulogu i vezu na audit_day ako je potrebno
                to_update = []
                if res.role != role:
                    res.role = role
                    to_update.append('role')
                desired_day = day_by_date.get(d)
                if res.audit_day_id != (desired_day.id if desired_day else None):
                    res.audit_day = desired_day
                    to_update.append('audit_day')
                if to_update:
                    res.save(update_fields=to_update)
    
    def save(self, *args, **kwargs):
        # Debug ispisi
        import logging
        logger = logging.getLogger('django')
        logger.info(f"CycleAudit.save pozvana za audit ID={self.pk}, tip={self.audit_type}, status={self.audit_status}, prethodni status={self._prev_audit_status}")
        
        # Proveravamo da li je status audita završen
        is_status_completed = self.audit_status == 'completed' and self._prev_audit_status != 'completed'
        logger.info(f"is_status_completed = {is_status_completed}")
        
        # Proveravamo da li je promenjen planirani datum
        is_planned_date_changed = self.planned_date != self._prev_planned_date
        logger.info(f"is_planned_date_changed = {is_planned_date_changed}")
        
        # Proveravamo da li je promenjen stvarni datum
        is_actual_date_changed = self.actual_date != self._prev_actual_date
        logger.info(f"is_actual_date_changed = {is_actual_date_changed}")
        
        # Proveravamo tip audita
        is_recertification = self.audit_type == 'recertification'
        is_surveillance_1 = self.audit_type == 'surveillance_1'
        is_surveillance_2 = self.audit_type == 'surveillance_2'
        logger.info(f"Tipovi audita: is_recertification={is_recertification}, is_surveillance_1={is_surveillance_1}, is_surveillance_2={is_surveillance_2}")
        logger.info(f"Actual date: {self.actual_date}")
        
        # Izvršavamo uobičajeno čuvanje
        logger.info("Pozivam super().save()")
        super().save(*args, **kwargs)
        logger.info("super().save() završen")
        
        # Ako je inicijalni audit završen ili je upravo unet/izmenjen stvarni datum,
        # propagiramo datum na ciklus i zakazujemo prvi nadzorni audit
        if self.audit_type == 'initial' and self.actual_date and (is_status_completed or is_actual_date_changed):
            try:
                cycle = self.certification_cycle
                prev_cycle_actual = cycle.datum_sprovodjenja_inicijalne
                if prev_cycle_actual != self.actual_date:
                    cycle.datum_sprovodjenja_inicijalne = self.actual_date
                    # Snimamo ciklus da bismo aktivirali ensure_first_surveillance_scheduled preko save()
                    cycle.save(update_fields=['datum_sprovodjenja_inicijalne'])
                else:
                    # Ako je već postavljen isti datum, ipak osiguramo zakazivanje
                    cycle.ensure_first_surveillance_scheduled()
            except Exception:
                # Ne blokiramo dalji tok u slučaju greške
                pass
        # Ako je resertifikacioni audit završen i postoji stvarni datum,
        # kreiramo (idempotentno) novi ciklus sertifikacije u skladu sa formulom
        # Trigerujemo ako je došlo do prelaza u 'completed' ili je promenjen actual_date dok je status već 'completed'.
        # Proveravamo da li je postavljen flag _skip_cycle_creation (koristi se tokom importa)
        skip_cycle_creation = getattr(self, '_skip_cycle_creation', False)
        if is_recertification and self.actual_date and self.audit_status == 'completed' and (is_status_completed or is_actual_date_changed) and not skip_cycle_creation:
            # Umesto kreiranja novog ciklusa sertifikacije, dodajemo nove audite u postojeći ciklus
            self.certification_cycle.extend_with_new_audits(recertification_audit=self)
        
        # Ako je prvi nadzorni audit označen kao završen, kreiramo drugi nadzorni audit
        # Drugi nadzorni audit se kreira tek nakon što se sprovede stvarni datum prvog nadzornog audita
        # Proveravamo da li je postavljen flag _skip_cycle_creation (koristi se tokom importa)
        elif is_status_completed and is_surveillance_1 and self.actual_date and not skip_cycle_creation:
            # Formula: Drugi nadzor = Prvi nadzorni audit (stvarni datum) + 1 godina - Broj dana nadzora
            from datetime import timedelta
            cycle = self.certification_cycle
            
            # Zaokružujemo broj_dana_nadzora na veći ceo broj ako ima decimalni deo .5 ili veći
            if cycle.broj_dana_nadzora:
                broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_nadzora)
                second_surveillance_date = self.actual_date + timedelta(days=365) - timedelta(days=broj_dana)
            else:
                second_surveillance_date = self.actual_date + timedelta(days=365)
            
            # Kreiramo drugi nadzorni audit
            CycleAudit.objects.get_or_create(
                certification_cycle=cycle,
                audit_type='surveillance_2',
                defaults={
                    'planned_date': second_surveillance_date,
                    'audit_status': 'planned'
                }
            )
        
        # Ako je drugi nadzorni audit označen kao završen ILI je upravo unet/izmenjen stvarni datum,
        # kreiramo ili ažuriramo planirani resertifikacioni audit
        # Proveravamo da li je postavljen flag _skip_cycle_creation (koristi se tokom importa)
        elif is_surveillance_2 and self.actual_date and (is_status_completed or is_actual_date_changed) and not skip_cycle_creation:
            # Resertifikacija = Drugi nadzorni audit Stvarni datum + 1 godina (- Broj dana resertifikacije ako je unet)
            from datetime import timedelta
            cycle = self.certification_cycle
            
            # Zaokružujemo broj_dana_resertifikacije na veći ceo broj ako ima decimalni deo .5 ili veći
            if cycle.broj_dana_resertifikacije:
                broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_resertifikacije)
                recertification_date = self.actual_date + timedelta(days=365) - timedelta(days=broj_dana)
            else:
                # Ako nije unet broj dana resertifikacije: Drugi nadzor Stvarni datum + 1 godina
                recertification_date = self.actual_date + timedelta(days=365)
            
            recert_audit, created = CycleAudit.objects.get_or_create(
                certification_cycle=cycle,
                audit_type='recertification',
                defaults={
                    'planned_date': recertification_date,
                    'audit_status': 'planned'
                }
            )
            if not created and recert_audit.planned_date != recertification_date:
                recert_audit.planned_date = recertification_date
                recert_audit.save(update_fields=['planned_date'])
        
        # Kreiramo dane audita ako je novi audit ili ako je promenjen planirani ili stvarni datum
        if self.pk is None or is_planned_date_changed or is_actual_date_changed:
            self.create_audit_days()
            logger.info("Kreirani dani audita")
            # Sinhronizujemo rezervacije auditora sa aktuelnim danima audita
            try:
                self.sync_auditor_reservations()
            except Exception:
                pass
        
        # Ažuriramo prethodne vrednosti
        self._prev_audit_status = self.audit_status
        self._prev_planned_date = self.planned_date
        self._prev_actual_date = self.actual_date
        logger.info(f"_prev_audit_status postavljen na {self._prev_audit_status}")
        logger.info(f"_prev_planned_date postavljen na {self._prev_planned_date}")
        logger.info(f"_prev_actual_date postavljen na {self._prev_actual_date}")
        logger.info("CycleAudit.save završena")
    
    def __str__(self):
        audit_type_display = dict(self.AUDIT_TYPE_CHOICES)[self.audit_type]
        return f"{self.certification_cycle.company.name} - {audit_type_display} ({self.planned_date.strftime('%Y-%m-%d')})"
