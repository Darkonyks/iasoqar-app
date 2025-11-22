from django import forms
from django.utils.translation import gettext_lazy as _
from .company_models import OstalaLokacija, Company

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
            'country': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Izvlačimo company_id iz kwargs ako je prosleđen
        company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        # Ako je prosleđen company_id, sakrivamo polje company i postavljamo vrednost
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                # Sakrivamo polje company iz forme
                self.fields['company'].widget = forms.HiddenInput()
                # Postavljamo inicijalnu vrednost
                self.fields['company'].initial = company
                # Ako je forma već instancirana (edit mode), postavljamo vrednost
                if not self.instance.pk:
                    self.instance.company = company
            except Company.DoesNotExist:
                pass
