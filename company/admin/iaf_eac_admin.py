from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ..models.iaf_eac import IAFEACCode
from ..models.company_iaf_eac import CompanyIAFEACCode

@admin.register(IAFEACCode)
class IAFEACCodeAdmin(admin.ModelAdmin):
    list_display = ('iaf_code', 'description')
    search_fields = ('iaf_code', 'description', 'sub_descriptors')
    list_filter = ('iaf_code',)
    ordering = ('iaf_code',)

class CompanyIAFEACCodeInline(admin.TabularInline):
    model = CompanyIAFEACCode
    extra = 1
    verbose_name = _("IAF/EAC Code")
    verbose_name_plural = _("IAF/EAC Codes")
    fields = ('iaf_eac_code', 'is_primary', 'notes')
    autocomplete_fields = ('iaf_eac_code',)

@admin.register(CompanyIAFEACCode)
class CompanyIAFEACCodeAdmin(admin.ModelAdmin):
    list_display = ('company', 'iaf_eac_code', 'is_primary')
    list_filter = ('is_primary', 'iaf_eac_code')
    search_fields = ('company__name', 'iaf_eac_code__iaf_code', 'iaf_eac_code__description')
    autocomplete_fields = ('company', 'iaf_eac_code')
