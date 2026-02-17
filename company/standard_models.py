from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .iaf_models import IAFScopeReference


class StandardDefinition(models.Model):
    """
    Model za definisanje standarda koji postoje u sistemu.
    Jedan standard može biti povezan sa više IAF Scope Reference-a.
    """
    STANDARD_CHOICES = [
        ('ISO 9001:2015', _('ISO 9001:2015 - Sistem menadžmenta kvalitetom')),
        ('ISO 14001:2015', _('ISO 14001:2015 - Sistem upravljanja zaštitom životne sredine')),
        ('ISO 45001:2018', _('ISO 45001:2018 - Sistem menadžmenta bezbednošću i zdravljem na radu')),
        ('ISO 27001:2022', _('ISO 27001:2022 - Sistem menadžmenta bezbednošću informacija')),
        ('ISO 22000:2018', _('ISO 22000:2018 - Sistem menadžmenta bezbednošću hrane')),
        ('ISO 13485:2016', _('ISO 13485:2016 - Medicinska sredstva - Sistem menadžmenta kvalitetom')),
        ('ISO 50001:2018', _('ISO 50001:2018 - Sistem menadžmenta energijom')),
        ('ISO 20000-1:2018', _('ISO 20000-1:2018 - Sistem menadžmenta IT uslugama')),
        ('ISO 22301:2019', _('ISO 22301:2019 - Sistem menadžmenta kontinuitetom poslovanja')),
        ('ISO 37001:2016', _('ISO 37001:2016 - Sistem menadžmenta protiv mita')),
        ('ISO 17025:2017', _('ISO 17025:2017 - Opšti zahtevi za kompetentnost laboratorija za ispitivanje i laboratorija za etaloniranje')),
        ('ISO 17020:2012', _('ISO 17020:2012 - Ocenjivanje usaglašenosti - Zahtevi za rad različitih tipova tela koja obavljaju kontrolisanje')),
        ('ISO 17021-1:2015', _('ISO 17021-1:2015 - Ocenjivanje usaglašenosti - Zahtevi za tela koja obavljaju proveru i sertifikaciju sistema menadžmenta')),
        ('ISO 17024:2012', _('ISO 17024:2012 - Ocenjivanje usaglašenosti - Opšti zahtevi za tela koja obavljaju sertifikaciju osoba')),
        ('ISO 17065:2012', _('ISO 17065:2012 - Ocenjivanje usaglašenosti - Zahtevi za tela koja sertifikuju proizvode, procese i usluge')),
        ('HACCP', _('HACCP - Sistem bezbednosti hrane')),
        ('FSSC 22000 v5.1', _('FSSC 22000 v5.1 - Sistem bezbednosti hrane')),
        ('IFS Food v7', _('IFS Food v7 - International Featured Standard Food')),
        ('BRC Food v9', _('BRC Food v9 - British Retail Consortium Global Standard for Food Safety')),
    ]

    code = models.CharField(_('Kod standarda'), max_length=20, unique=True)
    name = models.CharField(_('Naziv standarda'), max_length=100)
    standard = models.CharField(
        _('Standard'),
        max_length=100,
        choices=STANDARD_CHOICES,
        blank=True,
        null=True
    )
    description = models.TextField(_('Opis'), blank=True, null=True)
    active = models.BooleanField(_('Aktivan'), default=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    # Veza sa IAF Scope Reference
    iaf_scope_references = models.ManyToManyField(
        IAFScopeReference,
        through='StandardIAFScopeReference',
        related_name='standards',
        verbose_name=_('IAF Scope References')
    )

    class Meta:
        verbose_name = _("Definicija standarda")
        verbose_name_plural = _("Definicije standarda")
        ordering = ['code']

    def __str__(self):
        if self.standard:
            return f"{self.get_standard_display()}"
        return f"{self.code} - {self.name}"


class StandardIAFScopeReference(models.Model):
    """
    Model za povezivanje standarda sa IAF Scope Reference vrednostima.
    Jedan standard može biti povezan sa više IAF Scope Reference-a.
    """
    standard = models.ForeignKey(
        StandardDefinition,
        on_delete=models.CASCADE,
        related_name='standard_iaf_scope_references',
        verbose_name=_('Standard')
    )
    iaf_scope_reference = models.ForeignKey(
        IAFScopeReference,
        on_delete=models.CASCADE,
        related_name='iaf_scope_reference_standards',
        verbose_name=_('IAF Scope Reference')
    )
    is_primary = models.BooleanField(_('Primarni'), default=False)
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)
    
    class Meta:
        verbose_name = _('Standard IAF Scope Reference')
        verbose_name_plural = _('Standard IAF Scope References')
        unique_together = [['standard', 'iaf_scope_reference']]
        ordering = ['-is_primary', 'iaf_scope_reference__reference']
    
    def __str__(self):
        return f"{self.standard} - {self.iaf_scope_reference}"
    
    def save(self, *args, **kwargs):
        # Ako je ovaj označen kao primarni, osiguraj da nijedan drugi za ovaj standard nije primarni
        if self.is_primary:
            StandardIAFScopeReference.objects.filter(
                standard=self.standard, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        
        # Ako je ovo jedini za standard, označi ga kao primarni
        if not self.id and not StandardIAFScopeReference.objects.filter(standard=self.standard).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)


class CompanyStandard(models.Model):
    """
    Model za povezivanje kompanija sa standardima.
    Jedna kompanija može imati više standarda.
    """
    
    CERTIFICATE_STATUS_CHOICES = [
        ('active', _('Aktivan')),
        ('suspended', _('Suspendovan')),
        ('withdrawn', _('Povučen')),
        ('expired', _('Istekao')),
        ('pending', _('U procesu')),
    ]
    
    company = models.ForeignKey('Company', on_delete=models.CASCADE, verbose_name=_("Kompanija"), related_name='company_standards')
    standard = models.CharField(
        _("Standard (staro)"),
        max_length=100,
        choices=StandardDefinition.STANDARD_CHOICES,
        blank=True,
        null=True,
        help_text=_("Staro polje za standard, koristite standard_definition umesto ovog polja")
    )
    standard_definition = models.ForeignKey(
        StandardDefinition,
        on_delete=models.CASCADE,
        related_name='companies',
        verbose_name=_("Standard"),
        help_text=_("Izaberite standard iz liste definisanih standarda")
    )
    certificate_number = models.CharField(
        _('Broj sertifikata'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Broj sertifikata za ovaj standard')
    )
    certificate_status = models.CharField(
        _('Status sertifikata'),
        max_length=20,
        choices=CERTIFICATE_STATUS_CHOICES,
        default='pending',
        help_text=_('Status sertifikata za ovaj standard')
    )
    issue_date = models.DateField(_('Datum izdavanja'), blank=True, null=True)
    expiry_date = models.DateField(_('Datum isteka'), blank=True, null=True)
    notes = models.TextField(_('Napomene'), blank=True, null=True)
    created_at = models.DateTimeField(_('Kreirano'), default=timezone.now)
    updated_at = models.DateTimeField(_('Ažurirano'), auto_now=True)

    class Meta:
        verbose_name = _("Standard kompanije")
        verbose_name_plural = _("Standardi kompanija")
        ordering = ['-issue_date']
        unique_together = [['company', 'standard_definition']]

    def __str__(self):
        standard_name = self.standard_definition.name if self.standard_definition else self.standard
        return f"{self.company.name} - {standard_name}"


# Alias za kompatibilnost sa postojećim kodom
Standard = CompanyStandard
