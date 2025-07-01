from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime

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
    start_date = models.DateField(_('Datum početka ciklusa'), help_text=_('Datum inicijalne sertifikacije'))
    
    # Datum završetka ciklusa (3 godine nakon inicijalne sertifikacije)
    end_date = models.DateField(_('Datum završetka ciklusa'), null=True, blank=True, help_text=_('Datum isteka ciklusa (3 godine nakon inicijalne sertifikacije)'))
    
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
        ordering = ['-start_date']
    
    def __str__(self):
        status_display = dict(self.CYCLE_STATUS_CHOICES)[self.status]
        return f"{self.company.name} - {self.start_date.strftime('%Y-%m-%d')} do {self.end_date.strftime('%Y-%m-%d')} ({status_display})"
    
    def save(self, *args, **kwargs):
        # Automatski postavi end_date na 3 godine nakon start_date ako nije postavljen
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + datetime.timedelta(days=3*365)
            
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
        Automatski kreira potrebne audite za ciklus sertifikacije.
        Za prvi ciklus kreira inicijalni audit, a za sve cikluse kreira nadzorne i resertifikacioni audit.
        """
        from datetime import timedelta
        
        # Samo za prvi ciklus kreiramo inicijalni audit
        if is_first_cycle:
            # Inicijalni audit (već je obavljen na datum početka ciklusa)
            CycleAudit.objects.get_or_create(
                certification_cycle=self,
                audit_type='initial',
                defaults={
                    'planned_date': self.start_date,
                    'actual_date': self.start_date,
                    'audit_status': 'completed'
            }
        )
        
        # Prvi nadzorni (godinu dana nakon inicijalnog)
        first_surveillance_date = self.start_date + timedelta(days=365)
        CycleAudit.objects.get_or_create(
            certification_cycle=self,
            audit_type='surveillance_1',
            defaults={
                'planned_date': first_surveillance_date
            }
        )
        
        # Drugi nadzorni (dve godine nakon inicijalnog)
        second_surveillance_date = self.start_date + timedelta(days=2*365)
        CycleAudit.objects.get_or_create(
            certification_cycle=self,
            audit_type='surveillance_2',
            defaults={
                'planned_date': second_surveillance_date
            }
        )
        
        # Resertifikacija (tri godine nakon inicijalnog)
        recertification_date = self.start_date + timedelta(days=3*365 - 30)  # 30 dana pre isteka
        CycleAudit.objects.get_or_create(
            certification_cycle=self,
            audit_type='recertification',
            defaults={
                'planned_date': recertification_date
            }
        )
    
    def extend_with_new_audits(self, recertification_audit=None):
        """
        Produžava postojeći ciklus sertifikacije nakon što je završen resertifikacioni audit.
        Umesto kreiranja novog ciklusa, ažurira datume postojećeg ciklusa i dodaje nove audite.
        """
        from datetime import timedelta
        
        # Ako je završen resertifikacioni audit, produžavamo trajanje postojećeg ciklusa
        if recertification_audit and recertification_audit.actual_date:
            new_start_date = recertification_audit.actual_date
        else:
            # Ako nema stvarnog datuma, koristimo planirani datum ili trenutni datum
            if recertification_audit and recertification_audit.planned_date:
                new_start_date = recertification_audit.planned_date
            else:
                new_start_date = self.end_date
        
        # Produžavamo kraj ciklusa za još 3 godine od datuma resertifikacije
        self.end_date = new_start_date + timedelta(days=3*365)  # 3 godine od nove resertifikacije
        
        # Ažuriramo napomenu o produžetku ciklusa
        self.notes = f"{self.notes}\nCiklus produžen nakon resertifikacije {new_start_date.strftime('%Y-%m-%d')}. Novi kraj ciklusa: {self.end_date.strftime('%Y-%m-%d')}"
        
        # Sačuvamo promene u ciklusu
        self.save(update_fields=['end_date', 'notes'])
        
        # Kreiramo nove audite za produženi ciklus
        # Prvi nadzorni (godinu dana nakon resertifikacije)
        first_surveillance_date = new_start_date + timedelta(days=365)
        CycleAudit.objects.create(
            certification_cycle=self,
            audit_type='surveillance_1',
            planned_date=first_surveillance_date,
            audit_status='planned'
        )
        
        # Drugi nadzorni (dve godine nakon resertifikacije)
        second_surveillance_date = new_start_date + timedelta(days=2*365)
        CycleAudit.objects.create(
            certification_cycle=self,
            audit_type='surveillance_2',
            planned_date=second_surveillance_date,
            audit_status='planned'
        )
        
        # Nova resertifikacija (tri godine nakon prethodne)
        new_recertification_date = new_start_date + timedelta(days=3*365 - 30)  # 30 dana pre isteka
        CycleAudit.objects.create(
            certification_cycle=self,
            audit_type='recertification',
            planned_date=new_recertification_date,
            audit_status='planned'
        )
        
        return self
        
    def create_next_certification_cycle(self, recertification_audit=None):
        """
        Kreira novi ciklus sertifikacije nakon što je završen resertifikacioni audit.
        Kopira relevantne podatke iz tekućeg ciklusa i postavlja nove datume.
        
        U novom ciklusu se ne kreira inicijalni audit, samo nadzorni i resertifikacioni.
        
        Napomena: Ova metoda je zadržana zbog kompatibilnosti, ali se više ne koristi.
        Umesto nje se sada koristi extend_with_new_audits.
        """
        from datetime import timedelta
        
        # Prvo proverimo da li je ciklus već završen
        if self.status == 'completed':
            # Već je završen i verovatno je već kreiran novi ciklus
            return None
            
        # Uzmemo datum završetka resertifikacije kao datum početka novog ciklusa
        if recertification_audit and recertification_audit.actual_date:
            start_date = recertification_audit.actual_date
        else:
            # Ako nema stvarnog datuma, koristimo planirani datum ili trenutni datum
            if recertification_audit and recertification_audit.planned_date:
                start_date = recertification_audit.planned_date
            else:
                start_date = self.end_date
        
        # Kreiranje novog ciklusa
        new_cycle = CertificationCycle.objects.create(
            company=self.company,
            start_date=start_date,
            end_date=start_date + timedelta(days=3*365),  # 3 godine od novog početka
            is_integrated_system=self.is_integrated_system,
            inicijalni_broj_dana=self.inicijalni_broj_dana,
            broj_dana_nadzora=self.broj_dana_nadzora,
            broj_dana_resertifikacije=self.broj_dana_resertifikacije,
            # Prenosimo datum sprovođenja inicijalne samo kao referencu
            datum_sprovodjenja_inicijalne=self.datum_sprovodjenja_inicijalne,
            notes=f"Automatski kreiran nastavak ciklusa {self.start_date.strftime('%Y-%m-%d')} - {self.end_date.strftime('%Y-%m-%d')}"
        )
        
        # Kopiranje standarda iz trenutnog ciklusa u novi
        for cycle_standard in self.cycle_standards.all():
            CycleStandard.objects.create(
                certification_cycle=new_cycle,
                standard_definition=cycle_standard.standard_definition,
                company_standard=cycle_standard.company_standard
            )
        
        # Označimo trenutni ciklus kao završen
        self.status = 'completed'
        self.save(update_fields=['status'])
        
        # Kreiramo osnovne audite za novi ciklus
        # Napomena: is_first_cycle=False jer ovo nije prvi ciklus
        new_cycle.create_default_audits(is_first_cycle=False)
        
        return new_cycle

    def get_cycle_summary(self):
        """
        Generiše rezime ciklusa sa svim auditima i statusima.
        """
        audits = self.audits.all().order_by('planned_date')
        
        summary = {
            'company': self.company.name,
            'cycle_period': f"{self.start_date.strftime('%Y-%m-%d')} do {self.end_date.strftime('%Y-%m-%d')}",
            'status': dict(self.CYCLE_STATUS_CHOICES)[self.status],
            'is_integrated': 'Da' if self.is_integrated_system else 'Ne',
            'standards': [std.standard_definition.code for std in self.cycle_standards.all()],
            'audits': []
        }
        
        for audit in audits:
            audit_info = {
                'type': dict(audit.AUDIT_TYPE_CHOICES)[audit.audit_type],
                'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                'planned_date': audit.planned_date.strftime('%Y-%m-%d') if audit.planned_date else 'N/A',
                'actual_date': audit.actual_date.strftime('%Y-%m-%d') if audit.actual_date else 'N/A',
                'lead_auditor': audit.lead_auditor.ime_prezime if audit.lead_auditor else 'Nije dodeljen'
            }
            summary['audits'].append(audit_info)
        
        return summary


class CycleStandard(models.Model):
    """
    Model koji povezuje ciklus sertifikacije sa standardima koji su uključeni u taj ciklus.
    """
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
        return f"{self.certification_cycle.company.name} - {self.standard_definition.code} ({self.certification_cycle.start_date.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Nakon dodavanja standarda, proverimo da li je integrisani sistem
        self.certification_cycle.detect_integrated_system()


class CycleAudit(models.Model):
    """
    Model za pojedinačne audite u ciklusu sertifikacije.
    """
    AUDIT_TYPE_CHOICES = [
        ('initial', _('Inicijalni audit')),
        ('surveillance_1', _('Prvi nadzorni audit')),
        ('surveillance_2', _('Drugi nadzorni audit')),
        ('recertification', _('Resertifikacija')),
        ('special', _('Specijalni audit')),
    ]
    
    AUDIT_STATUS_CHOICES = [
        ('planned', _('Planirano')),
        ('in_progress', _('U toku')),
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
    # Uklonjena polja: completion_date, datum_sprovodjenja_inicijalne, inicijalni_broj_dana, broj_dana_nadzora, broj_dana_resertifikacije
    
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
    
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    # Pratimo prethodnu vrednost statusa audita za detekciju promene
    _prev_audit_status = None
    
    class Meta:
        verbose_name = _('Audit u ciklusu')
        verbose_name_plural = _('Auditi u ciklusu')
        ordering = ['planned_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Zapamtimo trenutni status za kasnije poređenje
        self._prev_audit_status = self.audit_status
    
    def save(self, *args, **kwargs):
        is_status_completed = self.audit_status == 'completed' and self._prev_audit_status != 'completed'
        is_recertification = self.audit_type == 'recertification'
        
        # Izvršavamo uobičajeno čuvanje
        super().save(*args, **kwargs)
        
        # Ako je resertifikacioni audit označen kao završen
        if is_status_completed and is_recertification:
            # Umesto kreiranja novog ciklusa sertifikacije, dodajemo nove audite u postojeći ciklus
            self.certification_cycle.extend_with_new_audits(recertification_audit=self)
        
        # Ažuriramo prethodnu vrednost statusa
        self._prev_audit_status = self.audit_status
        
    def __str__(self):
        audit_type_display = dict(self.AUDIT_TYPE_CHOICES)[self.audit_type]
        return f"{self.certification_cycle.company.name} - {audit_type_display} ({self.planned_date.strftime('%Y-%m-%d')})"
