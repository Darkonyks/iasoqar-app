from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from massadmin.massadmin import mass_change_selected
from django import forms
from django.core.exceptions import ValidationError
from .models import Company, OstalaLokacija, Standard, NaredneProvere, CalendarEvent, KontaktOsoba
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class AutoCalculateSecondDateField(forms.DateField):
    def clean(self, value):
        cleaned_value = super().clean(value)
        if cleaned_value and hasattr(self, 'instance') and self.instance:
            try:
                # Ako je ovo prvi nadzor održan, automatski postavi drugi nadzor
                if self.field_name == 'first_surv_cond':
                    company = self.instance.company
                    if company and company.audit_days_each:
                        audit_days = float(company.audit_days_each)
                        self.instance.second_surv_due = cleaned_value + timedelta(days=365) - timedelta(days=audit_days)
                        self.instance.save()
            except Exception as e:
                raise ValidationError(f"Greška pri računanju datuma: {e}")
        return cleaned_value

class NaredneProvereAdminForm(forms.ModelForm):
    first_surv_cond = forms.DateField(
        required=False,
        label=_("Prvi nadzor - održan"),
        widget=admin.widgets.AdminDateWidget()
    )

    class Meta:
        model = NaredneProvere
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['first_surv_cond'].instance = instance
            self.fields['first_surv_cond'].field_name = 'first_surv_cond'

    def clean_first_surv_cond(self):
        logger.info("Cleaning first_surv_cond field")
        cleaned_value = self.cleaned_data['first_surv_cond']
        logger.info(f"Cleaned value: {cleaned_value}")
        
        if cleaned_value and hasattr(self, 'instance') and self.instance:
            try:
                company = self.instance.company
                logger.info(f"Company: {company}")
                
                if company and company.audit_days_each:
                    audit_days = float(company.audit_days_each)
                    logger.info(f"Audit days: {audit_days}")
                    
                    # Prvo dodamo godinu dana
                    next_date = cleaned_value + timedelta(days=365)
                    logger.info(f"Date after adding 365 days: {next_date}")
                    
                    # Zatim oduzmemo broj dana za audit
                    next_date = next_date - timedelta(days=audit_days)
                    logger.info(f"Final calculated date: {next_date}")
                    
                    self.instance.second_surv_due = next_date
                    logger.info("Set second_surv_due on instance")
                else:
                    logger.warning("Company not found or audit_days_each not set")
            except Exception as e:
                logger.error(f"Error calculating date: {e}", exc_info=True)
                raise ValidationError(f"Greška pri računanju datuma: {e}")
        return cleaned_value

    def save(self, commit=True):
        logger.info("Saving form")
        instance = super().save(commit=False)
        if instance.first_surv_cond and not instance.second_surv_due:
            try:
                company = instance.company
                if company and company.audit_days_each:
                    audit_days = float(company.audit_days_each)
                    next_date = instance.first_surv_cond + timedelta(days=365) - timedelta(days=audit_days)
                    instance.second_surv_due = next_date
                    logger.info(f"Set second_surv_due in save: {next_date}")
            except Exception as e:
                logger.error(f"Error in save: {e}", exc_info=True)
        
        if commit:
            instance.save()
            logger.info("Instance saved")
        return instance

class OstalaLokacijaInline(admin.TabularInline):
    model = OstalaLokacija
    extra = 0
    fields = ['name', 'street', 'street_number', 'city', 'postal_code', 'phone', 'email']

class StandardInline(admin.TabularInline):
    model = Standard
    extra = 0
    fields = ['standard']

class NaredneProvereInline(admin.TabularInline):
    model = NaredneProvere
    extra = 0
    fields = ['first_surv_due', 'first_surv_cond', 'second_surv_due', 'second_surv_cond', 
              'trinial_audit_due', 'trinial_audit_cond', 'status']

class KontaktOsobaInline(admin.TabularInline):
    model = KontaktOsoba
    extra = 0
    fields = ['ime_prezime', 'pozicija', 'telefon', 'email', 'is_primary']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'pib', 'mb', 'city', 'industry', 'get_primary_contact', 'certificate_status', 'is_active']
    list_filter = [
        'is_active',
        'industry',
        'city',
        'certificate_status'
    ]
    search_fields = ['name', 'pib', 'mb', 'email', 'kontakt_osobe__ime_prezime']
    readonly_fields = ['created_at', 'updated_at', 'get_status_color']
    inlines = [KontaktOsobaInline, OstalaLokacijaInline, StandardInline, NaredneProvereInline]
    
    def get_primary_contact(self, obj):
        primary_contact = obj.kontakt_osobe.filter(is_primary=True).first()
        return primary_contact.ime_prezime if primary_contact else "-"
    get_primary_contact.short_description = _("Primarna kontakt osoba")
    
    fieldsets = [
        (_('Osnovni podaci'), {
            'fields': [('name', 'is_active'), ('pib', 'mb'), 'industry', 'number_of_employees']
        }),
        (_('Glavna lokacija'), {
            'fields': [('street', 'street_number'), ('city', 'postal_code'), 'country']
        }),
        (_('Kontakt informacije'), {
            'fields': ['phone', 'email', 'website']
        }),
        (_('Sertifikacija'), {
            'fields': [
                'certificate_status',
                'suspension_until_date',
                'initial_audit_conducted_date',
                ('audit_days', 'audit_days_each'),
                'visits_per_year'
            ]
        }),
        (_('Dodatne informacije'), {
            'fields': ['notes']
        }),
        (_('Sistemska polja'), {
            'fields': ['created_at', 'updated_at', 'get_status_color'],
            'classes': ['collapse']
        }),
    ]
    actions = [mass_change_selected]

@admin.register(OstalaLokacija)
class OstalaLokacijaAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'city', 'full_address', 'phone']
    list_filter = ['company', 'city']
    search_fields = ['name', 'company__name', 'street', 'city']
    actions = [mass_change_selected]

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ['company', 'standard']
    list_filter = ['standard', 'company']
    search_fields = ['company__name']
    actions = [mass_change_selected]
    
    fieldsets = [
        (_('Osnovni podaci'), {
            'fields': ['company', 'standard']
        }),
    ]

@admin.register(NaredneProvere)
class NaredneProvereAdmin(admin.ModelAdmin):
    form = NaredneProvereAdminForm
    list_display = ['company', 'get_next_audit_info', 'status', 'first_surv_cond', 'second_surv_due']
    list_filter = ['status', 'company']
    search_fields = ['company__name']
    actions = [mass_change_selected]

    def get_next_audit_info(self, obj):
        next_audit = obj.get_next_audit_date
        if next_audit:
            return f"{next_audit['type']} - {next_audit['date']}"
        return _("Nema zakazanih provera")
    get_next_audit_info.short_description = _("Sledeća provera")

    def save_model(self, request, obj, form, change):
        """Override save_model to ensure dates are calculated before saving"""
        logger.info(f"Saving NaredneProvere for company {obj.company}")
        
        if obj.first_surv_cond and not obj.second_surv_due:
            try:
                company = obj.company
                logger.info(f"Found company: {company}")
                
                if company and company.audit_days_each:
                    logger.info(f"audit_days_each: {company.audit_days_each}")
                    # Konvertujemo u float jer je DecimalField
                    audit_days = float(company.audit_days_each)
                    # Prvo dodamo godinu dana
                    next_date = obj.first_surv_cond + timedelta(days=365)
                    # Zatim oduzmemo broj dana za audit
                    next_date = next_date - timedelta(days=audit_days)
                    
                    logger.info(f"Calculated second_surv_due: {next_date}")
                    obj.second_surv_due = next_date
                else:
                    logger.warning("Company not found or audit_days_each not set")
            except Exception as e:
                logger.error(f"Error calculating date: {e}", exc_info=True)
        
        super().save_model(request, obj, form, change)
        # Proverimo da li je datum stvarno sačuvan
        logger.info(f"After save - second_surv_due: {obj.second_surv_due}")

    fieldsets = [
        (_('Osnovni podaci'), {
            'fields': ['company', 'status']
        }),
        (_('Prvi nadzor'), {
            'fields': ['first_surv_due', 'first_surv_cond']
        }),
        (_('Drugi nadzor'), {
            'fields': ['second_surv_due', 'second_surv_cond']
        }),
        (_('Resertifikacija'), {
            'fields': ['trinial_audit_due', 'trinial_audit_cond']
        }),
    ]

    class Media:
        js = ['admin/js/calendar.js']
        css = {
            'all': ['admin/css/forms.css']
        }

@admin.register(KontaktOsoba)
class KontaktOsobaAdmin(admin.ModelAdmin):
    list_display = ['ime_prezime', 'company', 'pozicija', 'telefon', 'email', 'is_primary']
    list_filter = ['is_primary', 'company']
    search_fields = ['ime_prezime', 'company__name', 'email']
    actions = [mass_change_selected]

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'naredne_provere', 'audit_type', 'start', 'end', 'all_day')
    list_filter = ('audit_type', 'all_day', 'start')
    search_fields = ('title', 'naredne_provere__company__name')
    raw_id_fields = ('naredne_provere',)
    date_hierarchy = 'start'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['start'].widget = admin.widgets.AdminSplitDateTime()
        form.base_fields['end'].widget = admin.widgets.AdminSplitDateTime()
        return form
