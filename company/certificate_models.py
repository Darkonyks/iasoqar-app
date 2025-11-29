from django.db import models
from django.utils.translation import gettext_lazy as _


class Certificate(models.Model):
    """
    Model za sertifikat kompanije.
    Jedna kompanija može imati više sertifikata sa različitim brojevima i statusima.
    Sertifikat se vezuje za kompaniju, ne za standarde.
    """
    
    # Status choices
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_EXPIRED = 'expired'
    STATUS_PENDING = 'pending'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Aktivan')),
        (STATUS_SUSPENDED, _('Suspendovan')),
        (STATUS_WITHDRAWN, _('Deregistrovan')),
        (STATUS_EXPIRED, _('Istekao')),
        (STATUS_PENDING, _('Na čekanju')),
        (STATUS_CANCELLED, _('Otkazan')),
    ]
    
    # Veza sa kompanijom
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_("Kompanija")
    )
    
    # Broj sertifikata
    certificate_number = models.CharField(
        _("Broj sertifikata"),
        max_length=100,
        unique=True,
        help_text=_("Jedinstveni broj sertifikata")
    )
    
    # Status sertifikata
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    
    # Datum suspenzije (ako je suspendovan)
    suspension_until_date = models.DateField(
        _("Suspenzija do datuma"),
        blank=True,
        null=True
    )
    
    # Datum izdavanja sertifikata
    issue_date = models.DateField(
        _("Datum izdavanja"),
        blank=True,
        null=True
    )
    
    # Datum isteka sertifikata
    expiry_date = models.DateField(
        _("Datum isteka"),
        blank=True,
        null=True
    )
    
    # Napomene
    notes = models.TextField(
        _("Napomene"),
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(_("Kreirano"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Ažurirano"), auto_now=True)
    
    class Meta:
        verbose_name = _("Sertifikat")
        verbose_name_plural = _("Sertifikati")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.certificate_number} - {self.company.name} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Proverava da li je sertifikat aktivan"""
        return self.status == self.STATUS_ACTIVE
    
    @property
    def is_suspended(self):
        """Proverava da li je sertifikat suspendovan"""
        return self.status == self.STATUS_SUSPENDED
