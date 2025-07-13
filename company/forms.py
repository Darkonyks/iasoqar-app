from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Company, IAFEACCode, CompanyIAFEACCode
from .cycle_models import CycleAudit, CertificationCycle
from .cycle_models import CertificationCycle, CycleStandard, CycleAudit
from .standard_models import StandardDefinition, CompanyStandard
from .auditor_models import Auditor
from .audit_utils import is_auditor_qualified_for_company, is_auditor_qualified_for_audit
from datetime import datetime, timedelta, date
import json

class AuditForm(forms.ModelForm):
    """Nova verzija forme za audite koja koristi CycleAudit model umesto NaredneProvere"""
    class Meta:
        model = CycleAudit
        fields = [
            'certification_cycle',
            'audit_type',
            'planned_date',
            'actual_date',
            'audit_status',
            'lead_auditor',
            'report_number',
            'findings',
            'recommendations',
            'notes'
        ]
        widgets = {
            'certification_cycle': forms.Select(attrs={'class': 'form-control'}),
            'audit_type': forms.Select(attrs={'class': 'form-control'}),
            'audit_status': forms.Select(attrs={'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lead_auditor': forms.Select(attrs={'class': 'form-control'}),
            'report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class CertificationCycleForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje ciklusa sertifikacije"""
    
    cycle_type = forms.ChoiceField(
        choices=[
            ('initial', _('Inicijalni ciklus')),
            ('recertification', _('Resertifikacioni ciklus')),
        ],
        label=_('Tip ciklusa'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    standards = forms.ModelMultipleChoiceField(
        queryset=StandardDefinition.objects.none(),  # Empty queryset initially, will be set in __init__
        required=True,
        label=_('Standardi'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    # Polja za inicijalni audit
    initial_audit_date = forms.DateField(
        required=True,
        label=_('Datum inicijalnog audita'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    lead_auditor = forms.ModelChoiceField(
        queryset=Auditor.objects.all(),
        required=False,
        label=_('Vodeći auditor'),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    report_number = forms.CharField(
        max_length=100,
        required=False,
        label=_('Broj izveštaja'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CertificationCycle
        fields = [
            'company', 'end_date', 'datum_sprovodjenja_inicijalne',
            'status', 'is_integrated_system',
            'inicijalni_broj_dana',
            'broj_dana_nadzora',
            'broj_dana_resertifikacije',
            'notes'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'datum_sprovodjenja_inicijalne': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_integrated_system': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inicijalni_broj_dana': forms.NumberInput(attrs={'class': 'form-control'}),
            'broj_dana_nadzora': forms.NumberInput(attrs={'class': 'form-control'}),
            'broj_dana_resertifikacije': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dobijamo kompaniju iz inicijalnih podataka ili iz instance
        instance = kwargs.get('instance')
        initial_data = kwargs.get('initial', {})
        company_id = initial_data.get('company')
        
        if instance:
            # Ako je instanca već kreirana, popunjavamo polje standards sa postojećim standardima
            self.initial['standards'] = StandardDefinition.objects.filter(
                certification_cycles__certification_cycle=instance
            )
            company_id = instance.company_id
            
            # Inicijalizujemo initial_audit_date sa start_date instance
            if instance.start_date:
                self.initial['initial_audit_date'] = instance.start_date
                
            # Pokušavamo da dobijemo podatke o inicijalnom auditu
            try:
                initial_audit = instance.audits.get(audit_type='initial')
                if initial_audit:
                    if initial_audit.lead_auditor:
                        self.initial['lead_auditor'] = initial_audit.lead_auditor.id
                    if initial_audit.report_number:
                        self.initial['report_number'] = initial_audit.report_number
            except:
                pass
            
        # Filtriramo standarde samo za one koji su dodeljeni kompaniji i nemaju već dodeljen ciklus
        if company_id:
            # Prvo dobijamo sve standarde kompanije
            company_standards = CompanyStandard.objects.filter(company_id=company_id)
            standard_ids = company_standards.values_list('standard_definition_id', flat=True)
            
            # Zatim dobijamo sve standarde koji su već u nekom ciklusu za ovu kompaniju
            # (osim trenutnog ciklusa ako je u pitanju ažuriranje)
            exclude_cycle_id = instance.id if instance else None
            
            # Standardi koji su već dodeljeni nekom ciklusu
            used_standard_ids = set()
            cycles = CertificationCycle.objects.filter(company_id=company_id)
            if exclude_cycle_id:
                cycles = cycles.exclude(id=exclude_cycle_id)
                
            for cycle in cycles:
                cycle_standard_ids = CycleStandard.objects.filter(
                    certification_cycle=cycle
                ).values_list('standard_definition_id', flat=True)
                used_standard_ids.update(cycle_standard_ids)
            
            # Filtriramo samo standarde koji su dodeljeni kompaniji i nisu u drugim ciklusima
            available_standard_ids = [std_id for std_id in standard_ids if std_id not in used_standard_ids]
            
            # Postavljamo queryset za standards polje
            self.fields['standards'].queryset = StandardDefinition.objects.filter(
                id__in=available_standard_ids
            )
        else:
            # Ako nema kompanije, prikazujemo praznu listu
            self.fields['standards'].queryset = StandardDefinition.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        initial_audit_date = cleaned_data.get('initial_audit_date')
        end_date = cleaned_data.get('end_date')
        
        # Automatski postavi end_date na 3 godine nakon initial_audit_date ako nije postavljen
        if initial_audit_date and not end_date:
            cleaned_data['end_date'] = initial_audit_date.replace(year=initial_audit_date.year + 3)
        
        # Proveri da li je end_date nakon initial_audit_date
        if initial_audit_date and end_date and end_date <= initial_audit_date:
            self.add_error('end_date', _('Datum završetka mora biti nakon datuma inicijalnog audita'))
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Dobijamo podatke o inicijalnom auditu iz forme
        initial_audit_date = self.cleaned_data.get('initial_audit_date')
        lead_auditor = self.cleaned_data.get('lead_auditor')
        report_number = self.cleaned_data.get('report_number')
        
        # Ako je postavljen datum inicijalnog audita, koristimo ga kao start_date i datum_sprovodjenja_inicijalne
        if initial_audit_date:
            instance.start_date = initial_audit_date
            # Eksplicitno postavljamo datum_sprovodjenja_inicijalne na isti datum
            instance.datum_sprovodjenja_inicijalne = initial_audit_date
        else:
            # Ako nema datuma inicijalnog audita, ne možemo nastaviti
            raise forms.ValidationError(_('Datum inicijalnog audita je obavezan.'))
        
        if commit:
            instance.save()
            
            # Sačuvaj standarde
            standards = self.cleaned_data.get('standards')
            if standards:
                # Ukloni postojeće standarde koji nisu u novom setu
                current_standards = set(CycleStandard.objects.filter(
                    certification_cycle=instance
                ).values_list('standard_definition_id', flat=True))
                
                new_standards = set(std.id for std in standards)
                
                # Obriši standarde koji više nisu u listi
                for std_id in current_standards - new_standards:
                    CycleStandard.objects.filter(
                        certification_cycle=instance,
                        standard_definition_id=std_id
                    ).delete()
                
                # Dodaj nove standarde
                for std in standards:
                    if std.id not in current_standards:
                        # Pokušaj da nađemo company_standard za ovaj standard
                        company_standard = None
                        try:
                            company_standard = instance.company.company_standards.get(
                                standard_definition=std
                            )
                        except:
                            pass
                        
                        CycleStandard.objects.create(
                            certification_cycle=instance,
                            standard_definition=std,
                            company_standard=company_standard
                        )
            
            # Ako je novi ciklus, kreiraj default audite
            if not CycleAudit.objects.filter(certification_cycle=instance).exists():
                instance.create_default_audits(is_first_cycle=True)
                
                # Ažuriraj inicijalni audit sa podacima iz forme
                try:
                    initial_audit = CycleAudit.objects.get(
                        certification_cycle=instance,
                        audit_type='initial'
                    )
                    
                    # Postavi podatke iz forme
                    initial_audit.planned_date = initial_audit_date
                    initial_audit.actual_date = initial_audit_date
                    initial_audit.audit_status = 'completed'
                    
                    if lead_auditor:
                        initial_audit.lead_auditor = lead_auditor
                    
                    if report_number:
                        initial_audit.report_number = report_number
                    
                    initial_audit.save()
                except CycleAudit.DoesNotExist:
                    pass
        
        return instance


class CycleAuditForm(forms.ModelForm):
    """Forma za kreiranje i ažuriranje audita u ciklusu sertifikacije"""
    
    audit_team = forms.ModelMultipleChoiceField(
        queryset=Auditor.objects.all(),
        required=False,
        label=_('Tim auditora'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    class Meta:
        model = CycleAudit
        fields = [
            'certification_cycle', 'audit_type', 'audit_status',
            'planned_date', 'actual_date', 'audit_team',
            'lead_auditor', 'report_number', 'findings',
            'recommendations', 'notes', 'poslat_izvestaj'
        ]
        widgets = {
            'certification_cycle': forms.Select(attrs={'class': 'form-control'}),
            'audit_type': forms.Select(attrs={'class': 'form-control'}),
            'audit_status': forms.Select(attrs={'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lead_auditor': forms.Select(attrs={'class': 'form-control'}),
            'report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Sačuvaj request objekat ako je prosleđen
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        
        # Ako je instanca već kreirana, popunjavamo polje audit_team sa postojećim auditorima
        instance = kwargs.get('instance')
        if instance:
            self.initial['audit_team'] = instance.audit_team.all()
            
            # Onemogući promenu tipa audita za postojeći audit, ali sačuvaj originalnu vrednost
            # Koristimo readonly umesto disabled jer disabled polja ne šalju vrednost u zahtevu
            self.fields['audit_type'].widget.attrs['readonly'] = True
            # Dodatno sakrij polje audit_type da bi bilo nemoguće promeniti ga
            self.fields['audit_type'].widget.attrs['style'] = 'pointer-events: none;'
            
            # Ograniči lead_auditor samo na kvalifikovane auditore
            if instance.certification_cycle_id:
                qualified_auditors = Auditor.objects.filter(id__in=[
                    auditor.id for auditor in Auditor.objects.all()
                    if is_auditor_qualified_for_audit(auditor.id, instance.id)[0]
                ])
                self.fields['lead_auditor'].queryset = qualified_auditors
    
    def clean(self):
        cleaned_data = super().clean()
        lead_auditor = cleaned_data.get('lead_auditor')
        certification_cycle = cleaned_data.get('certification_cycle')
        actual_date = cleaned_data.get('actual_date')
        audit_status = cleaned_data.get('audit_status')
        
        # Automatski postavi status na 'completed' ako je unet stvarni datum
        if actual_date and audit_status == 'planned':
            cleaned_data['audit_status'] = 'completed'
            # Dodaj informativnu poruku koja će biti prikazana korisniku
            from django.contrib import messages
            messages.info(self.request, 'Status audita je automatski postavljen na "Završeno" jer je unet stvarni datum.')
        
        # Proveri da li je lead_auditor kvalifikovan za audit
        if lead_auditor and certification_cycle and self.instance.pk:
            is_qualified, missing_standards = is_auditor_qualified_for_audit(lead_auditor.id, self.instance.pk)
            if not is_qualified:
                missing_codes = ', '.join([std.code for std in missing_standards])
                self.add_error('lead_auditor', _(f'Auditor nije kvalifikovan za standarde: {missing_codes}'))
        
        return cleaned_data
    
    def save(self, commit=True):
        # Debug ispisi
        import logging
        logger = logging.getLogger('django')
        logger.info(f"CycleAuditForm.save pozvana za audit ID={self.instance.pk if self.instance.pk else 'novi'}")
        
        # Zapamtimo prethodni status audita pre nego što ga promenimo
        if self.instance.pk:
            # Učitamo sveži objekat iz baze da bismo imali tačan prethodni status
            from .cycle_models import CycleAudit
            original_audit = CycleAudit.objects.get(pk=self.instance.pk)
            prev_status = original_audit.audit_status
            logger.info(f"Učitan original iz baze: ID={original_audit.pk}, status={original_audit.audit_status}")
        else:
            prev_status = None
            logger.info("Novi audit, nema prethodnog statusa")
        
        # Novi status koji će biti postavljen
        new_status = self.cleaned_data.get('audit_status')
        logger.info(f"Novi status koji će biti postavljen: {new_status}")
        
        instance = super().save(commit=False)
        
        # Postavimo prethodni status da bi metoda save u modelu mogla da detektuje promenu
        instance._prev_audit_status = prev_status
        logger.info(f"Postavljam _prev_audit_status={prev_status} na instanci")
        
        # Provera da li je ovo prvi nadzorni audit koji se završava
        is_surveillance_1 = instance.audit_type == 'surveillance_1'
        is_status_completed = new_status == 'completed' and prev_status != 'completed'
        logger.info(f"Provera za kreiranje drugog nadzora: is_surveillance_1={is_surveillance_1}, is_status_completed={is_status_completed}")
        
        # Provera da li je postavljen stvarni datum
        actual_date = self.cleaned_data.get('actual_date')
        logger.info(f"Stvarni datum: {actual_date}")
        
        if commit:
            # Pozivamo originalnu save metodu modela koja će kreirati sledeće audite ako je potrebno
            logger.info("Pozivam instance.save() iz forme")
            instance.save()
            logger.info("instance.save() završen")
            
            # Direktno kreiraj drugi nadzorni audit ako je potrebno (dodatna provera)
            if is_surveillance_1 and is_status_completed and actual_date:
                logger.info("Dodatna provera: Pokušavam direktno kreirati drugi nadzorni audit")
                from datetime import timedelta
                from .cycle_models import CycleAudit, zaokruzi_na_veci_broj
                
                cycle = instance.certification_cycle
                if cycle.broj_dana_nadzora:
                    broj_dana = zaokruzi_na_veci_broj(cycle.broj_dana_nadzora)
                    second_surveillance_date = actual_date + timedelta(days=365) - timedelta(days=broj_dana)
                else:
                    second_surveillance_date = actual_date + timedelta(days=365)
                
                # Proveri da li već postoji drugi nadzorni audit
                existing = CycleAudit.objects.filter(
                    certification_cycle=cycle,
                    audit_type='surveillance_2'
                ).exists()
                
                if not existing:
                    logger.info(f"Kreiram drugi nadzorni audit sa planiranim datumom {second_surveillance_date}")
                    CycleAudit.objects.create(
                        certification_cycle=cycle,
                        audit_type='surveillance_2',
                        planned_date=second_surveillance_date,
                        audit_status='planned'
                    )
                else:
                    logger.info("Drugi nadzorni audit već postoji")
            
            # Sačuvaj tim auditora
            audit_team = self.cleaned_data.get('audit_team')
            if audit_team is not None:
                instance.audit_team.clear()
                instance.audit_team.add(*audit_team)
        
        logger.info("CycleAuditForm.save završena")
        return instance
