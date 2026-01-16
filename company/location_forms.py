from django import forms
from django.utils.translation import gettext_lazy as _
from .company_models import OstalaLokacija, Company

class LocationForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje ostalih lokacija kompanije"""
    
    class Meta:
        model = OstalaLokacija
        fields = [
            'company', 'name', 'street', 'street_number', 'city', 'postal_code', 'country', 'notes'
        ]
        widgets = {
            'company': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite naziv lokacije'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite ulicu'
            }),
            'street_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite broj'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite grad'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite poštanski broj'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite državu'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dodatne napomene (opciono)'
            })
        }
        labels = {
            'name': 'Naziv lokacije',
            'street': 'Ulica',
            'street_number': 'Broj',
            'city': 'Grad',
            'postal_code': 'Poštanski broj',
            'country': 'Država',
            'notes': 'Napomena'
        }
    
    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        # Postavi podrazumevanu vrednost za državu
        if not self.instance.pk and not self.initial.get('country'):
            self.initial['country'] = 'Srbija'
        
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                self.fields['company'].widget = forms.HiddenInput()
                self.fields['company'].initial = company
                if not self.instance.pk:
                    self.instance.company = company
            except Company.DoesNotExist:
                pass
