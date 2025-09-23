from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
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

    # Direct IAF/EAC codes assignment (for Technical Experts)
    iaf_eac_codes = models.ManyToManyField(
        IAFEACCode,
        through='AuditorIAFEACCode',
        related_name='auditori_direktni',
        verbose_name=_('IAF/EAC kodovi (TE)'),
        blank=True
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

    def clean(self):
        """Enforce mutual exclusivity between standards and direct IAF/EAC codes
        depending on auditor category.
        - Technical Expert: cannot have standards; uses direct IAF/EAC codes only
        - Others (lead_auditor/auditor/trainer): cannot have direct IAF/EAC codes
        """
        super().clean()

        # On unsaved instances, skip DB queries
        if not self.pk:
            return

        # Check existing links
        has_standards = AuditorStandard.objects.filter(auditor=self).exists()
        has_direct_codes = AuditorIAFEACCode.objects.filter(auditor=self).exists()

        if self.kategorija == self.CATEGORY_TECHNICAL_EXPERT:
            if has_standards:
                raise ValidationError(_('Tehnički ekspert ne može imati dodeljene standarde; dodeljuju se direktno IAF/EAC kodovi.'))
        else:
            if has_direct_codes:
                raise ValidationError(_('Samo tehnički ekspert može imati direktno dodeljene IAF/EAC kodove.'))

    def save(self, *args, **kwargs):
        # Ensure validations run on save
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_effective_iaf_eac_codes(self):
        """
        Returns a queryset of IAF/EAC codes applicable to this auditor:
        - For Technical Experts: direct codes via AuditorIAFEACCode
        - For others: codes linked through their standards via AuditorStandardIAFEACCode
        """
        if self.kategorija == self.CATEGORY_TECHNICAL_EXPERT:
            return IAFEACCode.objects.filter(auditor_direct_links__auditor=self).distinct()
        return IAFEACCode.objects.filter(auditor_standard_links__auditor_standard__auditor=self).distinct()


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
        try:
            auditor_name = self.auditor.ime_prezime if getattr(self, 'auditor_id', None) else '—'
        except Exception:
            auditor_name = '—'
        try:
            standard_str = str(self.standard) if getattr(self, 'standard_id', None) else '—'
        except Exception:
            standard_str = '—'
        return f"{auditor_name} - {standard_str}"

    def clean(self):
        super().clean()
        # Forbid assigning standards to Technical Experts
        # During ModelForm validation, auditor may not be set yet; guard on auditor_id
        if getattr(self, 'auditor_id', None):
            if self.auditor and self.auditor.kategorija == Auditor.CATEGORY_TECHNICAL_EXPERT:
                raise ValidationError(_('Tehnički ekspert ne može imati dodeljene standarde.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


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
        try:
            std_link = str(self.auditor_standard) if getattr(self, 'auditor_standard_id', None) else '—'
        except Exception:
            std_link = '—'
        try:
            code_str = str(self.iaf_eac_code) if getattr(self, 'iaf_eac_code_id', None) else '—'
        except Exception:
            code_str = '—'
        return f"{std_link} - {code_str}"
    
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


class AuditorIAFEACCode(models.Model):
    """
    Direct linking of IAF/EAC codes to an Auditor. Used only for Technical Experts.
    """
    auditor = models.ForeignKey(
        Auditor,
        on_delete=models.CASCADE,
        related_name='direct_iaf_links',
        verbose_name=_('Auditor')
    )
    iaf_eac_code = models.ForeignKey(
        IAFEACCode,
        on_delete=models.CASCADE,
        related_name='auditor_direct_links',
        verbose_name=_('IAF/EAC kod')
    )
    is_primary = models.BooleanField(_('Primarni kod'), default=False)
    notes = models.TextField(_('Napomene'), blank=True, null=True)

    class Meta:
        verbose_name = _('IAF/EAC kod auditora (TE)')
        verbose_name_plural = _('IAF/EAC kodovi auditora (TE)')
        unique_together = [['auditor', 'iaf_eac_code']]
        ordering = ['-is_primary', 'iaf_eac_code__iaf_code']

    def __str__(self):
        try:
            auditor_name = self.auditor.ime_prezime if getattr(self, 'auditor_id', None) else '—'
        except Exception:
            auditor_name = '—'
        try:
            code_str = str(self.iaf_eac_code) if getattr(self, 'iaf_eac_code_id', None) else '—'
        except Exception:
            code_str = '—'
        return f"{auditor_name} - {code_str}"

    def clean(self):
        super().clean()
        # Only Technical Expert can have direct IAF/EAC codes
        if self.auditor and self.auditor.kategorija != Auditor.CATEGORY_TECHNICAL_EXPERT:
            raise ValidationError(_('Samo tehnički ekspert može imati direktno dodeljene IAF/EAC kodove.'))

    def save(self, *args, **kwargs):
        # Ensure only one primary per auditor
        self.full_clean()
        if self.is_primary:
            AuditorIAFEACCode.objects.filter(
                auditor=self.auditor,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)
