from django import forms
from .company_models import OstalaLokacija, Company

# Placeholder-i za polja forme
FIELD_PLACEHOLDERS = {
    'name': 'Unesite naziv lokacije',
    'street': 'Unesite ulicu',
    'street_number': 'Unesite broj',
    'city': 'Unesite grad',
    'postal_code': 'Unesite poštanski broj',
    'country': 'Unesite državu',
    'notes': 'Dodatne napomene (opciono)',
}

FIELD_LABELS = {
    'name': 'Naziv lokacije',
    'street': 'Ulica',
    'street_number': 'Broj',
    'city': 'Grad',
    'postal_code': 'Poštanski broj',
    'country': 'Država',
    'notes': 'Napomena',
}

DEFAULT_COUNTRY = 'Srbija'


class LocationForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje ostalih lokacija kompanije."""

    class Meta:
        model = OstalaLokacija
        fields = [
            'company', 'name', 'street', 'street_number',
            'city', 'postal_code', 'country', 'notes',
        ]
        labels = FIELD_LABELS

    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        self._company_from_param = None

        self._apply_bootstrap_classes()
        self._set_default_country()
        self._bind_company(company_id)

    # ------------------------------------------------------------------
    # Privatne pomoćne metode
    # ------------------------------------------------------------------

    def _apply_bootstrap_classes(self):
        """Doda 'form-control' klasu i placeholder na svako vidljivo polje."""
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            field.widget.attrs.setdefault('class', 'form-control')
            if field_name in FIELD_PLACEHOLDERS:
                field.widget.attrs.setdefault('placeholder', FIELD_PLACEHOLDERS[field_name])
            # Textarea za napomene
            if field_name == 'notes' and not isinstance(field.widget, forms.Textarea):
                field.widget = forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': FIELD_PLACEHOLDERS.get('notes', ''),
                })
            elif field_name == 'notes':
                field.widget.attrs.setdefault('rows', 3)

    def _set_default_country(self):
        """Postavi podrazumevanu državu za nove instance."""
        if not self.instance.pk and not self.initial.get('country'):
            self.initial['country'] = DEFAULT_COUNTRY

    def _bind_company(self, company_id):
        """Poveži formu sa konkretnom kompanijom ako je prosleđen ID."""
        if not company_id:
            return
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return

        self._company_from_param = company
        self.fields['company'].widget = forms.HiddenInput()
        self.fields['company'].required = False
        self.fields['company'].initial = company
        if not self.instance.pk:
            self.instance.company = company

    # ------------------------------------------------------------------
    # Validacija
    # ------------------------------------------------------------------

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if company is None and self._company_from_param is not None:
            return self._company_from_param
        return company
