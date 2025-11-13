from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# IAF Scope Reference i povezani modeli
class IAFScopeReference(models.Model):
    """
    Model za IAF Scope Reference vrednosti koje se koriste za kategorizaciju standarda i IAF/EAC kodova.
    """
    reference = models.CharField(_('IAF Scope Reference'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)

    class Meta:
        verbose_name = _("IAF Scope Reference")
        verbose_name_plural = _("IAF Scope References")
        ordering = ['reference']

    def __str__(self):
        return f"{self.reference} - {self.description}" if self.description else self.reference


class IAFEACCode(models.Model):
    """
    Model for storing IAF (International Accreditation Forum) / EAC (Economic Activity Codes)
    These codes are used to categorize organizations by their economic activities
    for certification purposes.
    """
    iaf_scope_reference = models.ForeignKey(
        IAFScopeReference,
        on_delete=models.CASCADE,
        related_name='iaf_eac_codes',
        verbose_name=_("IAF Scope Reference"),
        null=True,  # Dozvoljavamo null zbog migracije postojećih podataka
    )
    iaf_code = models.CharField(_("IAF/EAC Code"), max_length=50, default="N/A")
    description = models.TextField(_("Code Description"), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)

    class Meta:
        verbose_name = _("IAF/EAC Code")
        verbose_name_plural = _("IAF/EAC Codes")
        ordering = ['iaf_code']

    def __str__(self):
        return f"{self.iaf_code} - {self.description}"



# StandardIAFScopeReference model je premešten u standard_models.py


# Standard model je premešten u standard_models.py


# Povezivanje kompanije sa IAF/EAC kodovima
class CompanyIAFEACCode(models.Model):
    """
    Model za povezivanje kompanije sa IAF/EAC kodovima.
    Jedna kompanija može imati više IAF/EAC kodova.
    """
    company = models.ForeignKey('Company', on_delete=models.CASCADE, verbose_name=_("Kompanija"), related_name='iaf_eac_codes')
    iaf_eac_code = models.ForeignKey(
        IAFEACCode,
        on_delete=models.CASCADE,
        related_name='companies',
        verbose_name=_("IAF/EAC Code")
    )
    is_primary = models.BooleanField(_('Primarni kod'), default=False)
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)

    class Meta:
        verbose_name = _("Kompanija IAF/EAC kod")
        verbose_name_plural = _("Kompanija IAF/EAC kodovi")
        unique_together = [['company', 'iaf_eac_code']]
        ordering = ['-is_primary', 'iaf_eac_code__iaf_code']

    def __str__(self):
        return f"{self.company.name} - {self.iaf_eac_code}"
    
    def save(self, *args, **kwargs):
        # Ako je ovaj kod označen kao primarni, osiguraj da nijedan drugi kod za ovu kompaniju nije primarni
        if self.is_primary:
            CompanyIAFEACCode.objects.filter(
                company=self.company, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        
        # Ako je ovo jedini kod za kompaniju, označi ga kao primarni
        if not self.id and not CompanyIAFEACCode.objects.filter(company=self.company).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)
