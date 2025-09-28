from django import forms
from .auditor_models import AuditorIAFEACCode
from .iaf_models import IAFEACCode

class DirectIAFEACCodeForm(forms.Form):
    """Forma za direktno dodeljivanje IAF/EAC koda tehničkom ekspertu"""
    iaf_eac_code = forms.ModelChoiceField(
        queryset=IAFEACCode.objects.all().order_by('iaf_code'),
        label='IAF/EAC kod',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_primary = forms.BooleanField(
        required=False,
        label='Primarni kod',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        required=False,
        label='Napomene',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
