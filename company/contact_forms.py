from django import forms
from .models import KontaktOsoba

class KontaktOsobaForm(forms.ModelForm):
    """
    Forma za kreiranje i ažuriranje kontakt osoba
    """
    class Meta:
        model = KontaktOsoba
        fields = ['ime_prezime', 'pozicija', 'email', 'telefon', 'is_primary']
        
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Dodavanje klasa za stilizovanje
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Checkbox polje ne treba form-control klasu
        self.fields['is_primary'].widget.attrs['class'] = 'form-check-input'
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.company and not instance.company_id:
            instance.company = self.company
            
        if commit:
            instance.save()
            
        return instance
