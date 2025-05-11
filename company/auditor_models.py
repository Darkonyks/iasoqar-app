from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .standard_models import StandardDefinition
from .iaf_models import IAFEACCode

class Auditor(models.Model):
    CATEGORY_LEAD_AUDITOR = 'lead_auditor'
    CATEGORY_AUDITOR = 'auditor'
    CATEGORY_TECHNICAL_EXPERT = 'technical_expert'
    CATEGORY_TRAINER = 'trainer'
    
    AUDITOR_CATEGORY_CHOICES = [
        (CATEGORY_LEAD_AUDITOR, _('Lead auditor')),
        (CATEGORY_AUDITOR, _('Auditor')),
        (CATEGORY_TECHNICAL_EXPERT, _('Tehnički ekspert')),
        (CATEGORY_TRAINER, _('Trainer')),
    ]
    
    # Basic Information
    ime_prezime = models.CharField(_('Ime i prezime'), max_length=200)
    email = models.EmailField(_('Email'))
    telefon = models.CharField(_('Broj telefona'), max_length=50)
    
    # Category
    kategorija = models.CharField(
        _('Kategorija'),
        max_length=50,
        choices=AUDITOR_CATEGORY_CHOICES,
        default=CATEGORY_AUDITOR
    )
    
    # Standards - korišćenje StandardDefinition modela
    standardi = models.ManyToManyField(
        StandardDefinition,
        through='AuditorStandard',
        related_name='auditori',
        verbose_name=_('Standardi')
    )
    
    # System fields
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    class Meta:
        verbose_name = _('Auditor')
        verbose_name_plural = _('Auditori')
        ordering = ['ime_prezime']
    
    def __str__(self):
        return f"{self.ime_prezime} ({self.get_kategorija_display()})"


class AuditorStandard(models.Model):
    """Model za povezivanje auditora sa standardima za koje je potpisan"""
    auditor = models.ForeignKey(
        Auditor, 
        on_delete=models.CASCADE,
        related_name='auditor_standardi',
        verbose_name=_('Auditor')
    )
    standard = models.ForeignKey(
        StandardDefinition,  # Koristimo StandardDefinition model
        on_delete=models.CASCADE,
        related_name='standard_auditori',
        verbose_name=_('Standard')
    )
    datum_potpisivanja = models.DateField(_('Datum potpisivanja'), blank=True, null=True)
    napomena = models.TextField(_('Napomena'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    # IAF/EAC kodovi povezani sa ovim standardom auditora
    iaf_eac_kodovi = models.ManyToManyField(
        IAFEACCode,
        through='AuditorStandardIAFEACCode',
        related_name='auditor_standardi',
        verbose_name=_('IAF/EAC kodovi')
    )
    
    class Meta:
        verbose_name = _('Standard auditora')
        verbose_name_plural = _('Standardi auditora')
        unique_together = [['auditor', 'standard']]
        ordering = ['-datum_potpisivanja']
    
    def __str__(self):
        return f"{self.auditor.ime_prezime} - {self.standard}"


class AuditorStandardIAFEACCode(models.Model):
    """
    Model za povezivanje standarda auditora sa IAF/EAC kodovima.
    Ovo omogućava da svaki standard koji auditor ima može biti povezan sa više IAF/EAC kodova.
    """
    auditor_standard = models.ForeignKey(
        AuditorStandard,
        on_delete=models.CASCADE,
        related_name='iaf_eac_links',
        verbose_name=_('Standard auditora')
    )
    iaf_eac_code = models.ForeignKey(
        IAFEACCode,
        on_delete=models.CASCADE,
        related_name='auditor_standard_links',
        verbose_name=_('IAF/EAC kod')
    )
    is_primary = models.BooleanField(_('Primarni kod'), default=False)
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('IAF/EAC kod standarda auditora')
        verbose_name_plural = _('IAF/EAC kodovi standarda auditora')
        unique_together = [['auditor_standard', 'iaf_eac_code']]
        ordering = ['-is_primary', 'iaf_eac_code__iaf_code']
    
    def __str__(self):
        return f"{self.auditor_standard} - {self.iaf_eac_code}"
    
    def save(self, *args, **kwargs):
        # Ako je ovaj kod označen kao primarni, osiguraj da nijedan drugi kod za ovaj standard auditora nije primarni
        if self.is_primary:
            AuditorStandardIAFEACCode.objects.filter(
                auditor_standard=self.auditor_standard, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        
        # Ako je ovo jedini kod za standard auditora, označi ga kao primarni
        if not self.id and not AuditorStandardIAFEACCode.objects.filter(auditor_standard=self.auditor_standard).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)
