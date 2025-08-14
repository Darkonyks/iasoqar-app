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
        status_display = dict(self.CYCLE_STATUS_CHOICES)[self.status]
        return f"{self.company.name} - {self.planirani_datum.strftime('%Y-%m-%d')} ({status_display})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nakon snimanja proverimo i ažuriramo status integrisanog sistema
        self.detect_integrated_system()
    
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
        Automatski kreira inicijalni audit i prvi nadzorni audit za ciklus sertifikacije.
        Za prvi ciklus kreira inicijalni audit, a zatim prvi nadzorni audit prema formuli.
        """
        from datetime import timedelta
        
        # Samo za prvi ciklus kreiramo inicijalni audit
        if is_first_cycle:
            # Inicijalni audit (već je obavljen na datum početka ciklusa)
            initial_audit, created = CycleAudit.objects.get_or_create(
                certification_cycle=self,
                audit_type='initial',
                defaults={
                    'planned_date': self.planirani_datum,
                    'actual_date': self.planirani_datum,
                    'audit_status': 'completed'
                }
            )
            
            # Ako imamo datum sprovođenja inicijalne provere i broj dana nadzora, kreiramo prvi nadzorni audit
            if self.datum_sprovodjenja_inicijalne and self.broj_dana_nadzora:
                # Zaokružujemo broj_dana_nadzora na veći ceo broj ako ima decimalni deo .5 ili veći
                broj_dana = zaokruzi_na_veci_broj(self.broj_dana_nadzora)
                # Prvi nadzor = Datum sprovođenja inicijelne provere - Broj dana nadzora + 1 godina
                first_surveillance_date = self.datum_sprovodjenja_inicijalne + timedelta(days=365) - timedelta(days=broj_dana)
                CycleAudit.objects.get_or_create(
                    certification_cycle=self,
                    audit_type='surveillance_1',
                    defaults={
                        'planned_date': first_surveillance_date
                    }
                )
            else:
                # Ako nemamo potrebne podatke, koristimo standardnu formulu (godinu dana nakon inicijalnog)
                first_surveillance_date = self.planirani_datum + timedelta(days=365)
                CycleAudit.objects.get_or_create(
                    certification_cycle=self,
                    audit_type='surveillance_1',
                    defaults={
                        'planned_date': first_surveillance_date
                    }
                )
    
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
        
        # Kreiramo novi ciklus sertifikacije
        new_cycle = CertificationCycle.objects.create(
            company=self.company,
            is_integrated_system=self.is_integrated_system,
            planirani_datum=new_start_date,
            datum_sprovodjenja_inicijalne=new_start_date,  # Postavljamo datum sprovođenja inicijalne na početak novog ciklusa
            status='active',
            inicijalni_broj_dana=self.inicijalni_broj_dana,
            broj_dana_nadzora=self.broj_dana_nadzora,
            broj_dana_resertifikacije=self.broj_dana_resertifikacije,
            notes=f"Novi ciklus kreiran nakon završetka prethodnog ciklusa. Početak: {new_start_date.strftime('%Y-%m-%d')}"
        )
        logger.info(f"Kreiran novi ciklus {new_cycle.id} sa početkom {new_start_date}")
        
        # Kopiramo standarde iz starog ciklusa u novi
        for cycle_standard in self.cycle_standards.all():
            CycleStandard.objects.create(
                certification_cycle=new_cycle,
                standard_definition=cycle_standard.standard_definition,
                company_standard=cycle_standard.company_standard,
                notes=cycle_standard.notes
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
        
        CycleAudit.objects.create(
            certification_cycle=new_cycle,
            audit_type='surveillance_1',
            planned_date=first_surveillance_date,
            audit_status='planned'
        )
        logger.info(f"Kreiran prvi nadzorni audit za novi ciklus {new_cycle.id} sa planiranim datumom {first_surveillance_date}")
        
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
        ('in_progress', _('U toku')),
        ('completed', _('Završeno')),
        ('cancelled', _('Otkazano')),
        ('postponed', _('Odloženo')),
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
    
    def create_audit_days(self):
        """
        Kreira dane audita na osnovu planiranog datuma i broja dana audita.
        Planirani dani se kreiraju unazad od planiranog datuma.
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
        
        logger.info(f"Kreiranje {broj_dana} dana audita za audit ID={self.pk}, tip={self.audit_type}, planirani datum={self.planned_date}")
        
        # Brišemo postojeće planirane dane audita
        self.audit_days.filter(is_planned=True, is_actual=False).delete()
        
        # Kreiramo nove planirane dane audita unazad od planiranog datuma
        audit_days = []
        for i in range(broj_dana):
            audit_date = self.planned_date - timedelta(days=i)
            audit_day = AuditDay(
                audit=self,
                date=audit_date,
                is_planned=True,
                is_actual=False
            )
            audit_days.append(audit_day)
        
        # Ako postoji stvarni datum, kreiramo i stvarne dane audita
        if self.actual_date:
            # Brišemo postojeće stvarne dane audita
            self.audit_days.filter(is_actual=True).delete()
            
            for i in range(broj_dana):
                audit_date = self.actual_date - timedelta(days=i)
                audit_day = AuditDay(
                    audit=self,
                    date=audit_date,
                    is_planned=False,
                    is_actual=True
                )
                audit_days.append(audit_day)
        
        # Čuvamo dane audita
        AuditDay.objects.bulk_create(audit_days)
        logger.info(f"Kreirano {len(audit_days)} dana audita")
    
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
        
        # Ako je resertifikacioni audit označen kao završen
        if is_status_completed and is_recertification:
            # Umesto kreiranja novog ciklusa sertifikacije, dodajemo nove audite u postojeći ciklus
            self.certification_cycle.extend_with_new_audits(recertification_audit=self)
        
        # Ako je prvi nadzorni audit označen kao završen, kreiramo drugi nadzorni audit
        # Drugi nadzorni audit se kreira tek nakon što se sprovede stvarni datum prvog nadzornog audita
        elif is_status_completed and is_surveillance_1 and self.actual_date:
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
        
        # Ako je drugi nadzorni audit označen kao završen, kreiramo resertifikacioni audit
        elif is_status_completed and is_surveillance_2 and self.actual_date:
            # Resertifikacija = Drugi nadzorni audit Stvarni datum - Broj dana resertifikacije + 1 godina
            from datetime import timedelta
            cycle = self.certification_cycle
            
            # Zaokružujemo broj_dana_resertifikacije na veći ceo broj ako ima decimalni deo .5 ili veći
            if cycle.broj_dana_resertifikacije:
                broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_resertifikacije)
                recertification_date = self.actual_date + timedelta(days=365) - timedelta(days=broj_dana)
            else:
                recertification_date = self.actual_date + timedelta(days=365) - timedelta(days=30)  # 30 dana pre isteka ako nemamo broj dana
            
            # Kreiramo resertifikacioni audit
            CycleAudit.objects.get_or_create(
                certification_cycle=cycle,
                audit_type='recertification',
                defaults={
                    'planned_date': recertification_date,
                    'audit_status': 'planned'
                }
            )
        
        # Kreiramo dane audita ako je novi audit ili ako je promenjen planirani datum ili stvarni datum
        if self.pk is None or is_planned_date_changed or self.actual_date:
            self.create_audit_days()
            logger.info("Kreirani dani audita")
        
        # Ažuriramo prethodne vrednosti
        self._prev_audit_status = self.audit_status
        self._prev_planned_date = self.planned_date
        logger.info(f"_prev_audit_status postavljen na {self._prev_audit_status}")
        logger.info(f"_prev_planned_date postavljen na {self._prev_planned_date}")
        logger.info("CycleAudit.save završena")
    
    def __str__(self):
        audit_type_display = dict(self.AUDIT_TYPE_CHOICES)[self.audit_type]
        return f"{self.certification_cycle.company.name} - {audit_type_display} ({self.planned_date.strftime('%Y-%m-%d')})"
