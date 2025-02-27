from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .data.serbia_cities import SERBIA_CITY_CHOICES
from .data.industries import INDUSTRY_CHOICES
from datetime import date, timedelta, datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

# Create your models here.

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
        (STATUS_WITHDRAWN, _('Povučen')),
        (STATUS_EXPIRED, _('Istekao')),
        (STATUS_PENDING, _('Na čekanju')),
        (STATUS_CANCELLED, _('Otkazan')),
    ]

    # Basic Information
    name = models.CharField(_("Naziv kompanije"), max_length=200)
    pib = models.CharField(_("PIB"), max_length=9, blank=True, null=True, validators=[
        RegexValidator(r'^\d{9}$', _('PIB mora sadržati tačno 9 cifara'))
    ])
    mb = models.CharField(_("Matični broj"), max_length=8, blank=True, null=True, validators=[
        RegexValidator(r'^\d{8}$', _('Matični broj mora sadržati tačno 8 cifara'))
    ])
    
    # Main Office Address
    street = models.CharField(_("Ulica"), max_length=200, blank=True, null=True)
    street_number = models.CharField(_("Broj"), max_length=20, blank=True, null=True)
    city = models.CharField(
        _("Grad"),
        max_length=50,
        choices=SERBIA_CITY_CHOICES,
        help_text=_("Izaberite grad"),
        blank=True,
        null=True
    )
    postal_code = models.CharField(_("Poštanski broj"), max_length=10, blank=True, null=True)
    country = models.CharField(_("Država"), max_length=100, default="Srbija")
    
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
    suspension_until_date = models.DateField(_("Suspenzija do datuma"), blank=True, null=True)
    audit_days = models.DecimalField(_("Broj dana audita"), max_digits=18, decimal_places=1, blank=True, null=True)
    initial_audit_conducted_date = models.DateField(_("Datum inicijalnog audita"), blank=True, null=True)
    visits_per_year = models.DecimalField(_("Poseta godišnje"), max_digits=18, decimal_places=0, blank=True, null=True)
    audit_days_each = models.DecimalField(_("Dana po auditu"), max_digits=18, decimal_places=1, blank=True, null=True)

    # Notes
    notes = models.TextField(_("Napomene"), blank=True, null=True)
    
    # System fields
    is_active = models.BooleanField(_("Aktivna"), default=True)
    created_at = models.DateTimeField(_("Kreirano"), auto_now_add=True)
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

    def get_status_color(self):
        """Returns Bootstrap color class based on certificate status"""
        status_colors = {
            self.STATUS_ACTIVE: 'success',
            self.STATUS_SUSPENDED: 'warning',
            self.STATUS_WITHDRAWN: 'danger',
            self.STATUS_EXPIRED: 'secondary',
            self.STATUS_PENDING: 'info',
            self.STATUS_CANCELLED: 'dark',
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
    telefon = models.CharField(_("Telefon"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    is_primary = models.BooleanField(_("Primarna kontakt osoba"), default=False)
    
    class Meta:
        verbose_name = _("Kontakt osoba")
        verbose_name_plural = _("Kontakt osobe")
        ordering = ['-is_primary', 'ime_prezime']

    def __str__(self):
        return f"{self.ime_prezime} ({self.company.name})"
    
    def save(self, *args, **kwargs):
        # Ako je ova osoba označena kao primarna, poništi primary flag za sve druge kontakte iste kompanije
        if self.is_primary:
            KontaktOsoba.objects.filter(company=self.company).exclude(pk=self.pk).update(is_primary=False)
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
    street = models.CharField(_("Ulica"), max_length=200)
    street_number = models.CharField(_("Broj"), max_length=20)
    city = models.CharField(
        _("Grad"),
        max_length=50,
        choices=SERBIA_CITY_CHOICES,
        help_text=_("Izaberite grad")
    )
    postal_code = models.CharField(_("Poštanski broj"), max_length=10)
    country = models.CharField(_("Država"), max_length=100, default="Srbija")
    phone = models.CharField(_("Telefon"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Ostala lokacija")
        verbose_name_plural = _("Ostale lokacije")
        ordering = ['name']
        # Add unique constraint to prevent duplicate locations
        unique_together = [['company', 'name']]

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def full_address(self):
        return f"{self.street} {self.street_number}, {self.city}"


class NaredneProvere(models.Model):
    AUDIT_STATUS_CHOICES = [
        ('pending', _('Na čekanju')),
        ('completed', _('Završeno')),
        ('delayed', _('Odlagano')),
        ('overdue', _('Isteklo')),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_("Kompanija"),
        related_name='naredne_provere'
    )
    first_surv_due = models.DateTimeField(
        _("Prvi nadzor - planiran"),
        null=True,
        blank=True
    )
    first_surv_cond = models.DateTimeField(
        _("Prvi nadzor - održan"),
        null=True,
        blank=True
    )
    second_surv_due = models.DateTimeField(
        _("Drugi nadzor - planiran"),
        null=True,
        blank=True
    )
    second_surv_cond = models.DateTimeField(
        _("Drugi nadzor - održan"),
        null=True,
        blank=True
    )
    trinial_audit_due = models.DateTimeField(
        _("Resertifikacija - planirana"),
        null=True,
        blank=True
    )
    trinial_audit_cond = models.DateTimeField(
        _("Resertifikacija - održana"),
        null=True,
        blank=True
    )
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=AUDIT_STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"{self.company.name} - Naredne provere"

    @property
    def get_next_audit_date(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dates = []
        
        if self.first_surv_due and self.first_surv_due.date() > today.date():
            dates.append(('Prvi nadzor', self.first_surv_due))
        if self.second_surv_due and self.second_surv_due.date() > today.date():
            dates.append(('Drugi nadzor', self.second_surv_due))
        if self.trinial_audit_due and self.trinial_audit_due.date() > today.date():
            dates.append(('Resertifikacija', self.trinial_audit_due))
        
        if dates:
            next_audit = min(dates, key=lambda x: x[1].date())
            return {'type': next_audit[0], 'date': next_audit[1]}
        return None

    @property
    def get_status_color(self):
        status_colors = {
            'pending': 'primary',
            'completed': 'success',
            'delayed': 'warning',
            'overdue': 'dark',
        }
        return status_colors.get(self.status, 'secondary')

    class Meta:
        verbose_name = _("Naredna provera")
        verbose_name_plural = _("Naredne provere")


class Standard(models.Model):
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

    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_("Kompanija"), related_name='standards')
    standard = models.CharField(_("Standard"), max_length=100, choices=STANDARD_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = _("Standard")
        verbose_name_plural = _("Standardi")
        ordering = ['-id']

    def __str__(self):
        return f"{self.get_standard_display()}"


class CalendarEvent(models.Model):
    title = models.CharField(_("Naslov"), max_length=200)
    start = models.DateTimeField(_("Početak"))
    end = models.DateTimeField(_("Kraj"), null=True, blank=True)
    all_day = models.BooleanField(_("Celodnevni događaj"), default=False)
    color = models.CharField(_("Boja"), max_length=20, default='#3c8dbc')
    naredne_provere = models.ForeignKey(
        NaredneProvere,
        on_delete=models.CASCADE,
        verbose_name=_("Naredne provere"),
        related_name='calendar_events',
        null=True,
        blank=True
    )
    audit_type = models.CharField(
        _("Tip provere"),
        max_length=50,
        choices=[
            ('first_surv', _('Prvi nadzor')),
            ('second_surv', _('Drugi nadzor')),
            ('trinial_audit', _('Resertifikacija')),
        ],
        null=True,
        blank=True
    )
    notes = models.TextField(_("Napomene"), blank=True, null=True)

    class Meta:
        verbose_name = _("Kalendarski događaj")
        verbose_name_plural = _("Kalendarski događaji")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Postavi end na kraj dana ako je all_day True
        if self.all_day and not self.end:
            self.end = self.start.replace(hour=23, minute=59, second=59)
        
        # Ažuriraj NaredneProvere datume
        if self.audit_type == 'first_surv':
            self.naredne_provere.first_surv_due = self.start.date()
        elif self.audit_type == 'second_surv':
            self.naredne_provere.second_surv_due = self.start.date()
        elif self.audit_type == 'trinial_audit':
            self.naredne_provere.trinial_audit_due = self.start.date()
        
        self.naredne_provere.save()
        super().save(*args, **kwargs)
