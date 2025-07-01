from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, timedelta, datetime
from .auditor_models import Auditor

# Model NaredneProvere je uklonjen jer je zamenjen sa CycleAudit modelom
# AUDIT_STATUS_CHOICES se zadržava jer se koristi na drugim mestima
AUDIT_STATUS_CHOICES = [
    ('pending', _('Na čekanju')),
    ('completed', _('Završeno')),
    ('delayed', _('Odlagano')),
    ('overdue', _('Isteklo')),
]


class CalendarEvent(models.Model):
    title = models.CharField(_("Naslov"), max_length=200)
    start = models.DateTimeField(_("Početak"))
    end = models.DateTimeField(_("Kraj"), null=True, blank=True)
    all_day = models.BooleanField(_("Celodnevni događaj"), default=False)
    color = models.CharField(_("Boja"), max_length=20, default='#3c8dbc')
    # Polje naredne_provere je uklonjeno jer je model NaredneProvere izbačen
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
        ordering = ['start']

    def __str__(self):
        return self.title


class Appointment(models.Model):
    """Model za zakazivanje sastanaka i termina"""
    
    # Tipovi sastanaka
    TYPE_MEETING = 'meeting'
    TYPE_AUDIT = 'audit'
    TYPE_TRAINING = 'training'
    TYPE_CONSULTATION = 'consultation'
    TYPE_OTHER = 'other'
    
    APPOINTMENT_TYPE_CHOICES = [
        (TYPE_MEETING, _('Sastanak')),
        (TYPE_AUDIT, _('Audit')),
        (TYPE_TRAINING, _('Trening')),
        (TYPE_CONSULTATION, _('Konsultacija')),
        (TYPE_OTHER, _('Ostalo')),
    ]
    
    # Statusi sastanaka
    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_POSTPONED = 'postponed'
    
    APPOINTMENT_STATUS_CHOICES = [
        (STATUS_SCHEDULED, _('Zakazan')),
        (STATUS_COMPLETED, _('Završen')),
        (STATUS_CANCELLED, _('Otkazan')),
        (STATUS_POSTPONED, _('Odložen')),
    ]
    
    # Basic Information
    title = models.CharField(_("Naslov"), max_length=200)
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE, 
        related_name='appointments',
        verbose_name=_("Kompanija")
    )
    appointment_type = models.CharField(
        _("Tip sastanka"), 
        max_length=50, 
        choices=APPOINTMENT_TYPE_CHOICES,
        default=TYPE_MEETING
    )
    
    # Date and Time
    start_datetime = models.DateTimeField(_("Vreme početka"))
    end_datetime = models.DateTimeField(_("Vreme završetka"), blank=True, null=True)
    all_day = models.BooleanField(_("Celodnevni događaj"), default=False)
    
    # Location
    location = models.CharField(_("Lokacija"), max_length=200, blank=True, null=True)
    is_online = models.BooleanField(_("Online sastanak"), default=False)
    meeting_link = models.URLField(_("Link za sastanak"), blank=True, null=True)
    
    # Attendees
    contact_persons = models.ManyToManyField(
        'KontaktOsoba',
        related_name='appointments',
        verbose_name=_("Kontakt osobe"),
        blank=True
    )
    external_attendees = models.TextField(
        _("Eksterni učesnici"), 
        blank=True, 
        null=True,
        help_text=_("Unesite imena i kontakte eksternih učesnika, jedan po liniji")
    )
    
    # Status and Notes
    status = models.CharField(
        _("Status"), 
        max_length=50, 
        choices=APPOINTMENT_STATUS_CHOICES,
        default=STATUS_SCHEDULED
    )
    notes = models.TextField(_("Napomene"), blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(_("Kreirano"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ažurirano"), auto_now=True)
    
    class Meta:
        verbose_name = _("Sastanak")
        verbose_name_plural = _("Sastanci")
        ordering = ['-start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.company.name} ({self.get_appointment_type_display()})"
    
    def get_status_color(self):
        """Returns Bootstrap color class based on appointment status"""
        status_colors = {
            self.STATUS_SCHEDULED: 'primary',
            self.STATUS_COMPLETED: 'success',
            self.STATUS_CANCELLED: 'danger',
            self.STATUS_POSTPONED: 'warning',
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_duration_in_hours(self):
        """Returns the duration of the appointment in hours"""
        if not self.end_datetime:
            return 0
        
        duration = self.end_datetime - self.start_datetime
        return duration.total_seconds() / 3600
    
    @property
    def calendar_event_data(self):
        """Returns data formatted for calendar display"""
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start_datetime.isoformat(),
            'end': self.end_datetime.isoformat() if self.end_datetime else None,
            'allDay': self.all_day,
            'color': self.get_status_color(),
            'url': f'/appointments/{self.id}/',
            'extendedProps': {
                'company': self.company.name,
                'type': self.get_appointment_type_display(),
                'status': self.get_status_display(),
                'location': self.location or 'Online' if self.is_online else 'N/A',
            }
        }
