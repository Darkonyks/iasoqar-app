from django.contrib import admin
from .company_models import Company

# Jednostavna admin klasa za Company model
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'pib', 'mb']

# Registracija Company modela
admin.site.register(Company, CompanyAdmin)
