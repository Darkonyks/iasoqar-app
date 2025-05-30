from django import forms
from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from .standard_models import StandardDefinition
from .iaf_models import IAFEACCode


class AuditorForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje auditora"""
    
    class Meta:
        model = Auditor
        fields = ['ime_prezime', 'email', 'telefon', 'kategorija']
        widgets = {
            'ime_prezime': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unesite ime i prezime'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Unesite email adresu'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unesite broj telefona'}),
            'kategorija': forms.Select(attrs={'class': 'form-control'}),
        }


class AuditorStandardForm(forms.ModelForm):
    """Forma za dodavanje standarda auditoru"""
    
    class Meta:
        model = AuditorStandard
        fields = ['standard', 'datum_potpisivanja', 'napomena']
        widgets = {
            'standard': forms.Select(attrs={'class': 'form-control'}),
            'datum_potpisivanja': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'napomena': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtriranje samo aktivnih standarda
        self.fields['standard'].queryset = StandardDefinition.objects.filter(active=True).order_by('code')


class AuditorStandardIAFEACForm(forms.ModelForm):
    """Forma za dodavanje IAF/EAC koda standardu auditora"""
    
    class Meta:
        model = AuditorStandardIAFEACCode
        fields = ['iaf_eac_code', 'is_primary', 'notes']
        widgets = {
            'iaf_eac_code': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['iaf_eac_code'].queryset = IAFEACCode.objects.all().order_by('iaf_code')
