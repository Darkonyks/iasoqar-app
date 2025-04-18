from django import forms
from .models import NaredneProvere, Company
from datetime import datetime, timedelta

class AuditForm(forms.ModelForm):
    class Meta:
        model = NaredneProvere
        fields = [
            'company', 'status',
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
            
        return cleaned_data
