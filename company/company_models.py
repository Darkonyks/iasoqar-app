from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .data.serbia_cities import SERBIA_CITY_CHOICES
from .data.industries import INDUSTRY_CHOICES
from .data.european_countries import EUROPEAN_COUNTRY_CHOICES
from datetime import date, timedelta


def validate_pib_optional(value):
    """Validator za PIB koji dozvoljava prazno polje ili tačno 9 cifara"""
    if value and not value.isdigit():
        raise ValidationError(_('PIB mora sadržati samo cifre'))
    if value and len(value) != 9:
        raise ValidationError(_('PIB mora sadržati tačno 9 cifara'))


def validate_mb_optional(value):
    """Validator za matični broj koji dozvoljava prazno polje ili tačno 8 cifara"""
    if value and not value.isdigit():
        raise ValidationError(_('Matični broj mora sadržati samo cifre'))
    if value and len(value) != 8:
        raise ValidationError(_('Matični broj mora sadržati tačno 8 cifara'))

class Company(models.Model):
    # Status choices
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_EXPIRED = 'expired'
    STATUS_PENDING = 'pending'
    STATUS_CANCELLED = 'cancelled'
    
    CERTIFICATE_STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Aktivan')),
        (STATUS_SUSPENDED, _('Suspendovan')),
        (STATUS_WITHDRAWN, _('Deregistrovan')),
        (STATUS_EXPIRED, _('Istekao')),
        (STATUS_PENDING, _('Na čekanju')),
        (STATUS_CANCELLED, _('Otkazan')),
    ]

    # Basic Information
    name = models.CharField(_("Naziv kompanije"), max_length=200)
    pib = models.CharField(_("PIB"), max_length=9, blank=True, null=True, validators=[validate_pib_optional])
    mb = models.CharField(_("Matični broj"), max_length=8, blank=True, null=True, validators=[validate_mb_optional])
    
    # Main Office Address
    street = models.CharField(_("Ulica"), max_length=200, blank=True, null=True)
    street_number = models.CharField(_("Broj"), max_length=20, blank=True, null=True)
    city = models.CharField(
        _("Grad"),
        max_length=100,
        help_text=_("Unesite grad"),
        blank=True,
        null=True
    )
    postal_code = models.CharField(_("Poštanski broj"), max_length=10, blank=True, null=True)
    country = models.CharField(
        _("Država"),
        max_length=100,
        default="Srbija",
        help_text=_("Unesite državu")
    )
    
    # Contact Information
    phone = models.CharField(_("Telefon"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    website = models.URLField(_("Web sajt"), blank=True, null=True)
    
    # Additional Information
    industry = models.CharField(
        _("Industrija"), 
        max_length=50, 
        choices=INDUSTRY_CHOICES,
        blank=True, 
        null=True,
        help_text=_("Izaberite industriju")
    )
    number_of_employees = models.IntegerField(_("Broj zaposlenih"), blank=True, null=True)

    # Certification Information
    certificate_status = models.CharField(
        _("Status sertifikata"), 
        max_length=50, 
        choices=CERTIFICATE_STATUS_CHOICES,
        default=STATUS_PENDING
    )
    certificate_number = models.CharField(_("Broj sertifikata"), max_length=100, blank=True, null=True)
    suspension_until_date = models.DateField(_("Suspenzija do datuma"), blank=True, null=True)

    # Registration Area
    oblast_registracije = models.TextField(_("Oblast registracije"), blank=True, null=True, help_text=_("Unesite oblast registracije kompanije"))
    
    # Notes
    notes = models.TextField(_("Napomene"), blank=True, null=True)
    
    # System fields
    is_active = models.BooleanField(_("Aktivna"), default=True)
    created_at = models.DateTimeField(_("Kreirano"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ažurirano"), auto_now=True)

    class Meta:
        verbose_name = _("Kompanija")
        verbose_name_plural = _("Kompanije")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (PIB: {self.pib})"

    @property
    def full_address(self):
        if not all([self.street, self.street_number, self.city]):
            return ""
        return f"{self.street} {self.street_number}, {self.city}"

    # Returns Bootstrap color class based on certificate status
    def get_status_color(self):
        status_colors = {
            self.STATUS_ACTIVE: 'success',
            self.STATUS_SUSPENDED: 'warning',
            self.STATUS_WITHDRAWN: 'danger',
            self.STATUS_EXPIRED: 'danger',
            self.STATUS_PENDING: 'info',
            self.STATUS_CANCELLED: 'secondary',
        }
        return status_colors.get(self.certificate_status, 'secondary')


class KontaktOsoba(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='kontakt_osobe',
        verbose_name=_("Kompanija")
    )
    ime_prezime = models.CharField(_("Ime i prezime"), max_length=200)
    pozicija = models.CharField(_("Pozicija"), max_length=200, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    telefon = models.CharField(_("Telefon"), max_length=50, blank=True, null=True)
    is_primary = models.BooleanField(_("Primarna kontakt osoba"), default=False)
    created_at = models.DateTimeField(_("Kreirano"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ažurirano"), auto_now=True)

    class Meta:
        verbose_name = _("Kontakt osoba")
        verbose_name_plural = _("Kontakt osobe")
        ordering = ['-is_primary', 'ime_prezime']

    def __str__(self):
        return f"{self.ime_prezime} ({self.company.name})"

    def save(self, *args, **kwargs):
        # Ako je ova osoba označena kao primarna, osiguraj da nijedna druga za ovu kompaniju nije primarna
        if self.is_primary:
            KontaktOsoba.objects.filter(company=self.company, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class OstalaLokacija(models.Model):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='ostale_lokacije', 
        verbose_name=_("Kompanija"),
        db_index=True  # Add index for better performance
    )
    name = models.CharField(_("Naziv lokacije"), max_length=200)
    street = models.CharField(_("Ulica"), max_length=200, blank=True, null=True)
    street_number = models.CharField(_("Broj"), max_length=20, blank=True, null=True)
    city = models.CharField(
        _("Grad"),
        max_length=100,
        blank=True,
        null=True
    )
    postal_code = models.CharField(_("Poštanski broj"), max_length=10, blank=True, null=True)
    country = models.CharField(
        _("Država"),
        max_length=100,
        default="Srbija",
        help_text=_("Unesite državu")
    )
    notes = models.TextField(_("Napomene"), blank=True, null=True)
    created_at = models.DateTimeField(_("Kreirano"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ažurirano"), auto_now=True)

    class Meta:
        verbose_name = _("Ostala lokacija")
        verbose_name_plural = _("Ostale lokacije")
        ordering = ['name']
        unique_together = [['company', 'name']]

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def full_address(self):
        if not all([self.street, self.street_number, self.city]):
            return ""
        return f"{self.street} {self.street_number}, {self.city}"
