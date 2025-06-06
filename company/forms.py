from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import NaredneProvere, Company, IAFEACCode, CompanyIAFEACCode
from .auditor_models import Auditor
from .audit_utils import is_auditor_qualified_for_company
from datetime import datetime, timedelta
import json

class AuditForm(forms.ModelForm):
    auditor = forms.ModelChoiceField(
        queryset=Auditor.objects.all(),
        required=False,
        label=_('Auditor'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = NaredneProvere
        fields = [
            'company', 'auditor', 'status',
            'first_surv_due', 'first_surv_cond',
            'second_surv_due', 'second_surv_cond',
            'trinial_audit_due', 'trinial_audit_cond',
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'first_surv_due': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'first_surv_cond': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'second_surv_due': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'second_surv_cond': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'trinial_audit_due': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'trinial_audit_cond': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all date fields optional
        for field_name in ['first_surv_due', 'first_surv_cond', 'second_surv_due', 
                          'second_surv_cond', 'trinial_audit_due', 'trinial_audit_cond']:
            self.fields[field_name].required = False
            
        # Format existing datetime values for the datetime-local input
        instance = kwargs.get('instance')
        if instance:
            for field_name in ['first_surv_due', 'first_surv_cond', 'second_surv_due', 
                              'second_surv_cond', 'trinial_audit_due', 'trinial_audit_cond']:
                field_value = getattr(instance, field_name)
                if field_value:
                    formatted_value = field_value.strftime('%Y-%m-%dT%H:%M')
                    self.initial[field_name] = formatted_value
    
    def clean(self):
        cleaned_data = super().clean()
        first_surv_due = cleaned_data.get('first_surv_due')
        
        # Auto-calculate second_surv_due and trinial_audit_due based on first_surv_due
        if first_surv_due and not cleaned_data.get('second_surv_due'):
            # Set second audit date to one year after first audit
            cleaned_data['second_surv_due'] = first_surv_due.replace(year=first_surv_due.year + 1)
            
        if first_surv_due and not cleaned_data.get('trinial_audit_due'):
            # Set recertification date to two years after first audit
            cleaned_data['trinial_audit_due'] = first_surv_due.replace(year=first_surv_due.year + 2)
        
        # Provera kvalifikacije auditora za kompaniju
        auditor = cleaned_data.get('auditor')
        company = cleaned_data.get('company')
        
        if auditor and company:
            is_qualified, missing_standards = is_auditor_qualified_for_company(auditor.id, company.id)
            if not is_qualified:
                missing_codes = ', '.join([std.code for std in missing_standards])
                raise ValidationError(
                    _('Auditor %(auditor)s nije kvalifikovan za standarde: %(standards)s'), 
                    code='invalid',
                    params={
                        'auditor': auditor.name,
                        'standards': missing_codes
                    }
                )
            
        return cleaned_data


class CompanyForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje kompanija sa podrškom za IAF/EAC kodove i standarde"""
    
    iaf_eac_codes_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    standards_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    deleted_standards = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Company
        fields = [
            # Osnovne informacije
            'name', 'pib', 'mb', 'industry', 'number_of_employees',
            'certificate_status', 'certificate_number',
            
            # Informacije o sertifikatu
            'suspension_until_date', 'audit_days', 'initial_audit_conducted_date',
            'visits_per_year', 'audit_days_each', 'oblast_registracije',
            
            # Adresa
            'street', 'street_number', 'city', 'postal_code',
            
            # Kontakt informacije
            'phone', 'email', 'website',
            
            # Dodatne informacije
            'notes'
        ]
        widgets = {
            # Datumska polja
            'initial_audit_conducted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'suspension_until_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Numerička polja
            'audit_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'visits_per_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'audit_days_each': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'number_of_employees': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Tekstualna polja
            'oblast_registracije': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Procesiranje IAF/EAC kodova ako su prosleđeni
            iaf_eac_data = self.cleaned_data.get('iaf_eac_codes_data')
            if iaf_eac_data:
                try:
                    iaf_eac_codes = json.loads(iaf_eac_data)
                    
                    # Ukloni sve postojeće kodove ako postoje novi
                    # Ovo nije najbolji pristup za performanse, ali osigurava tačnost
                    if iaf_eac_codes:
                        CompanyIAFEACCode.objects.filter(company=instance).delete()
                    
                    # Dodaj nove kodove
                    for code_data in iaf_eac_codes:
                        code_id = code_data.get('id')
                        is_primary = code_data.get('is_primary', False)
                        notes = code_data.get('notes', '')
                        
                        if code_id:
                            CompanyIAFEACCode.objects.create(
                                company=instance,
                                iaf_eac_code_id=code_id,
                                is_primary=is_primary,
                                notes=notes
                            )
                except (json.JSONDecodeError, Exception) as e:
                    # Logiraj grešku, ali nemoj prekinuti čuvanje
                    print(f"Error processing IAF/EAC codes: {e}")
            
            # Upravljanje standardima je prebačeno na posebne backend view funkcije
            # company_standard_create, company_standard_update i company_standard_delete
            # tako da ne treba da procesiramo standarde ovde
            pass
        
        return instance
