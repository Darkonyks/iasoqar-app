from django.contrib import admin
from django.utils.translation import gettext_lazy as _
import nested_admin

from ..cycle_models import CertificationCycle, CycleStandard, CycleAudit, AuditDay


class CycleStandardInline(nested_admin.NestedTabularInline):
    model = CycleStandard
    extra = 1
    fields = ['standard_definition', 'company_standard', 'notes']


class CycleAuditInline(nested_admin.NestedTabularInline):
    model = CycleAudit
    extra = 0
    fields = ['audit_type', 'audit_status', 'planned_date', 'actual_date', 'lead_auditor']
    readonly_fields = ['audit_type']  # Ne dozvoljavamo menjanje tipa audita jednom kad je kreiran


class CertificationCycleAdmin(nested_admin.NestedModelAdmin):
    list_display = ['company', 'planirani_datum', 'is_integrated_system', 'status']
    list_filter = ['status', 'is_integrated_system', 'planirani_datum']
    search_fields = ['company__name']
    date_hierarchy = 'planirani_datum'
    
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['company', 'planirani_datum', 'is_integrated_system', 'status', 'notes']
        })
    ]
    
    inlines = [CycleStandardInline, CycleAuditInline]
    
    actions = ['create_default_audits']
    
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
            'fields': ['planned_date', 'actual_date']
        }),
        ('Auditori', {
            'fields': ['lead_auditor', 'audit_team']
        }),
        ('Rezultati', {
            'fields': ['report_number', 'findings', 'recommendations', 'notes']
        })
    ]


class AuditDayAdmin(admin.ModelAdmin):
    list_display = ['audit', 'date', 'is_planned', 'is_actual']
    list_filter = ['is_planned', 'is_actual', 'date']
    search_fields = ['audit__certification_cycle__company__name']
    date_hierarchy = 'date'
    
    fieldsets = [
        ('Osnovne informacije', {
            'fields': ['audit', 'date']
        }),
        ('Status', {
            'fields': ['is_planned', 'is_actual', 'notes']
        })
    ]


# Registracija modela u admin panelu
admin.site.register(AuditDay, AuditDayAdmin)
