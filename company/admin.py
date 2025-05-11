from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Import svih modela
from .company_models import Company, KontaktOsoba, OstalaLokacija
from .iaf_models import IAFScopeReference, IAFEACCode, CompanyIAFEACCode
from .standard_models import StandardDefinition, StandardIAFScopeReference, CompanyStandard
from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from .calendar_models import NaredneProvere, CalendarEvent, Appointment
from .cycle_models import CertificationCycle, CycleAudit, CycleStandard

# Inline klase za model Company
class KontaktOsobaInline(admin.TabularInline):
    model = KontaktOsoba
    extra = 1
    fields = ['ime_prezime', 'pozicija', 'email', 'telefon', 'is_primary']

class OstalaLokacijaInline(admin.TabularInline):
    model = OstalaLokacija
    extra = 1
    fields = ['name', 'street', 'street_number', 'city', 'postal_code']

class CompanyStandardInline(admin.TabularInline):
    model = CompanyStandard
    extra = 1
    fields = ['standard_definition', 'issue_date', 'expiry_date', 'notes']

class CompanyIAFEACCodeInline(admin.TabularInline):
    model = CompanyIAFEACCode
    extra = 1
    fields = ['iaf_eac_code', 'is_primary']

# Admin klase
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'pib', 'mb', 'city']
    search_fields = ['name', 'pib', 'mb']
    list_filter = ['city', 'is_active']
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['name', 'pib', 'mb', 'industry', 'number_of_employees', 'certificate_status']
        }),
        ('Adresa', {
            'fields': ['street', 'street_number', 'city', 'postal_code', 'country']
        }),
        ('Kontakt informacije', {
            'fields': ['phone', 'email', 'website']
        }),
        ('Dodatne informacije', {
            'fields': ['notes', 'is_active']
        }),
    ]
    inlines = [KontaktOsobaInline, OstalaLokacijaInline, CompanyStandardInline, CompanyIAFEACCodeInline]

class KontaktOsobaAdmin(admin.ModelAdmin):
    list_display = ['ime_prezime', 'company', 'pozicija', 'email']

# Inline klase za model CertificationCycle
class CycleStandardInline(admin.TabularInline):
    model = CycleStandard
    extra = 1
    fields = ['standard_definition', 'company_standard', 'notes']

class CycleAuditInline(admin.TabularInline):
    model = CycleAudit
    extra = 1
    fields = ['audit_type', 'audit_status', 'planned_date', 'actual_date', 'completion_date', 'lead_auditor']

class CertificationCycleAdmin(admin.ModelAdmin):
    list_display = ['company', 'start_date', 'end_date', 'is_integrated_system', 'status']
    list_filter = ['status', 'is_integrated_system', 'start_date']
    search_fields = ['company__name']
    date_hierarchy = 'start_date'
    
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['company', 'start_date', 'end_date', 'is_integrated_system', 'status', 'notes']
        })
    ]
    
    inlines = [CycleStandardInline, CycleAuditInline]
    
    actions = ['create_default_audits_action']
    
    def create_default_audits_action(self, request, queryset):
        count = 0
        for cycle in queryset:
            cycle.create_default_audits()
            count += 1
        self.message_user(request, f"Kreirani podrazumevani auditi za {count} ciklus(a) sertifikacije.")
    create_default_audits_action.short_description = "Kreiraj podrazumevane audite za izabrane cikluse"

class CycleAuditAdmin(admin.ModelAdmin):
    list_display = ['certification_cycle', 'audit_type', 'audit_status', 'planned_date', 'actual_date', 'lead_auditor']
    list_filter = ['audit_type', 'audit_status', 'planned_date']
    search_fields = ['certification_cycle__company__name', 'lead_auditor__ime_prezime']
    date_hierarchy = 'planned_date'
    
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['certification_cycle', 'audit_type', 'audit_status']
        }),
        ('Datumi', {
            'fields': ['planned_date', 'actual_date', 'completion_date']
        }),
        ('Auditori', {
            'fields': ['lead_auditor', 'audit_team']
        }),
        ('Rezultati', {
            'fields': ['report_number', 'findings', 'recommendations', 'notes']
        })
    ]

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_datetime', 'status']
    list_filter = ['status', 'start_datetime', 'company']
    search_fields = ['title', 'company__name']
    date_hierarchy = 'start_datetime'
    
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['title', 'company', 'type', 'status']
        }),
        ('Vreme', {
            'fields': ['start_datetime', 'end_datetime', 'all_day']
        }),
        ('Lokacija', {
            'fields': ['location', 'is_online', 'meeting_link']
        }),
        ('Učesnici', {
            'fields': ['contact_persons', 'external_attendees']
        }),
        ('Dodatne informacije', {
            'fields': ['description', 'notes']
        })
    ]

# Registracija svih modela
admin.site.register(Company, CompanyAdmin)
admin.site.register(KontaktOsoba, KontaktOsobaAdmin)
admin.site.register(OstalaLokacija)
admin.site.register(IAFScopeReference)
admin.site.register(IAFEACCode)
admin.site.register(CompanyIAFEACCode)
admin.site.register(StandardDefinition)
admin.site.register(StandardIAFScopeReference)
admin.site.register(CompanyStandard)
admin.site.register(Auditor)
admin.site.register(AuditorStandard)
admin.site.register(AuditorStandardIAFEACCode)
admin.site.register(NaredneProvere)
admin.site.register(CalendarEvent)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(CertificationCycle, CertificationCycleAdmin)
admin.site.register(CycleStandard)
admin.site.register(CycleAudit)
