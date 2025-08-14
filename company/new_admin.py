from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import nested_admin
import sys

print("Loading new_admin.py", file=sys.stderr)

# Direct import all models
from company.company_models import Company, KontaktOsoba, OstalaLokacija
from company.iaf_models import IAFScopeReference, IAFEACCode, CompanyIAFEACCode
from company.standard_models import StandardDefinition, StandardIAFScopeReference, CompanyStandard
from company.auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from company.calendar_models import CalendarEvent, Appointment
from company.cycle_models import CertificationCycle, CycleStandard, CycleAudit

# Basic admin classes
class KontaktOsobaInline(admin.TabularInline):
    model = KontaktOsoba
    extra = 1

class OstalaLokacijaInline(admin.TabularInline):
    model = OstalaLokacija
    extra = 1

class StandardInline(admin.TabularInline):
    model = CompanyStandard
    extra = 1

class CompanyIAFEACCodeInline(admin.TabularInline):
    model = CompanyIAFEACCode
    extra = 1

class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'pib', 'mb', 'city']
    inlines = [KontaktOsobaInline, OstalaLokacijaInline, StandardInline, CompanyIAFEACCodeInline]

class IAFScopeReferenceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'description']

class StandardDefinitionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'standard']

class AuditorAdmin(admin.ModelAdmin):
    list_display = ['ime_prezime', 'email', 'telefon']

class CertificationCycleAdmin(admin.ModelAdmin):
    list_display = ['company', 'planirani_datum', 'is_integrated_system', 'status']

# Register all models
admin.site.register(Company, CompanyAdmin)
admin.site.register(KontaktOsoba)
admin.site.register(OstalaLokacija)
admin.site.register(IAFScopeReference, IAFScopeReferenceAdmin)
admin.site.register(IAFEACCode)
admin.site.register(CompanyIAFEACCode)
admin.site.register(StandardDefinition, StandardDefinitionAdmin)
admin.site.register(StandardIAFScopeReference)
admin.site.register(CompanyStandard)
admin.site.register(Auditor, AuditorAdmin)
admin.site.register(AuditorStandard)
admin.site.register(AuditorStandardIAFEACCode)
# Registracija NaredneProvere je uklonjena jer je model izbačen
admin.site.register(CalendarEvent)
admin.site.register(Appointment)
admin.site.register(CertificationCycle, CertificationCycleAdmin)
admin.site.register(CycleStandard)
admin.site.register(CycleAudit)

print("Finished registering all models in new_admin.py", file=sys.stderr)
