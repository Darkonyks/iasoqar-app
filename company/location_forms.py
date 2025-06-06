from django import forms
from django.utils.translation import gettext_lazy as _
from .company_models import OstalaLokacija

class LocationForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje ostalih lokacija kompanije"""
    
    class Meta:
        model = OstalaLokacija
        fields = [
            'company', 'name', 
            'street', 'street_number', 'city', 'postal_code', 'country',
            'notes'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'street_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
