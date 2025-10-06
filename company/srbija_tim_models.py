from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from .company_models import Company
from .auditor_models import Auditor
from .standard_models import StandardDefinition


class SrbijaTim(models.Model):
    """
    Model za evidenciju stvarnih poseta auditora (Crni kalendar).
    Predstavlja stvarne posete koje mogu odstupati od planiranih audit dana.
    """
    
    # Osnovne informacije o kompaniji
    certificate_number = models.CharField(
        _('Broj sertifikata'),
        max_length=100,
        help_text=_('Broj sertifikata kompanije')
    )
    
    # Veza sa Company modelom (obavezno)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='srbija_tim_visits',
        verbose_name=_('Kompanija'),
        help_text=_('Kompanija iz baze')
    )
    
    # Standardi - Many-to-Many veza
    standards = models.ManyToManyField(
        StandardDefinition,
        related_name='srbija_tim_visits',
        verbose_name=_('Standardi'),
        help_text=_('Standardi za koje se vrši audit')
    )
    
    # Datum isticanja sertifikata
    certificate_expiry_date = models.DateField(
        _('Datum isticanja sertifikata'),
        null=True,
        blank=True,
        help_text=_('Datum kada ističe sertifikat')
    )
    
    # Auditori - Many-to-Many veza
    auditors = models.ManyToManyField(
        Auditor,
        related_name='srbija_tim_visits',
        verbose_name=_('Auditori'),
        help_text=_('Auditori koji su učestvovali u poseti')
    )
    
    # Datum održanog sastanka
    visit_date = models.DateField(
        _('Datum održanog sastanka'),
        help_text=_('Datum kada je održan sastanak/poseta')
    )
    
    # Vreme održanog sastanka (opciono)
    visit_time = models.TimeField(
        _('Vreme održanog sastanka'),
        null=True,
        blank=True,
        help_text=_('Vreme kada je održan sastanak/poseta (opciono)')
    )
    
    # Status - Poslat izveštaj (checkbox)
    report_sent = models.BooleanField(
        _('Poslat izveštaj'),
        default=False,
        help_text=_('Da li je izveštaj poslat')
    )
    
    # Dodatne informacije
    notes = models.TextField(
        _('Napomene'),
        blank=True,
        null=True,
        help_text=_('Dodatne napomene o poseti')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_srbija_tim_visits',
        verbose_name=_('Kreirao')
    )
    
    class Meta:
        verbose_name = _('Srbija Tim - Poseta')
        verbose_name_plural = _('Srbija Tim - Posete')
        ordering = ['-visit_date', '-created_at']
        indexes = [
            models.Index(fields=['-visit_date']),
            models.Index(fields=['certificate_number']),
            models.Index(fields=['report_sent']),
        ]
    
    def __str__(self):
        return f"{self.certificate_number} - {self.company.name} ({self.visit_date})"
    
    def clean(self):
        """Validacija podataka"""
        super().clean()
        
        # Provera da li je datum posete u budućnosti (opciono upozorenje)
        if self.visit_date and self.visit_date > timezone.now().date():
            # Možete dodati upozorenje ili validaciju ako želite
            pass
        
        # Provera da li je datum isticanja sertifikata u prošlosti
        if self.certificate_expiry_date and self.certificate_expiry_date < timezone.now().date():
            # Možete dodati upozorenje
            pass
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_standards_display(self):
        """Vraća string sa svim standardima"""
        return ", ".join([std.code for std in self.standards.all()])
    
    def get_auditors_display(self):
        """Vraća string sa svim auditorima"""
        return ", ".join([auditor.ime_prezime for auditor in self.auditors.all()])
    
    def is_certificate_expired(self):
        """Proverava da li je sertifikat istekao"""
        if self.certificate_expiry_date:
            return self.certificate_expiry_date < timezone.now().date()
        return False
    
    def days_until_expiry(self):
        """Vraća broj dana do isticanja sertifikata"""
        if self.certificate_expiry_date:
            delta = self.certificate_expiry_date - timezone.now().date()
            return delta.days
        return None
