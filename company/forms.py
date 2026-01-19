from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import Company, IAFEACCode, CompanyIAFEACCode
from .cycle_models import CertificationCycle, CycleStandard, CycleAudit, AuditorReservation, zaokruzi_na_veci_broj
from .standard_models import StandardDefinition, CompanyStandard
from .auditor_models import Auditor
from .srbija_tim_models import SrbijaTim
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
            
            # Adresa
            'street', 'street_number', 'city', 'postal_code', 'country',
            
            # Kontakt informacije
            'phone', 'email', 'website',
            
            # Dodatne informacije
            'notes'
        ]
        widgets = {
            # Numerička polja
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
        label=_('Datum planiranog inicijalnog audita'),
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
            'company', 'datum_sprovodjenja_inicijalne',
            'status', 'is_integrated_system',
            'inicijalni_broj_dana',
            'broj_dana_nadzora',
            'broj_dana_resertifikacije',
            'notes'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
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

        # Ispravno dobijamo instancu i inicijalne vrednosti nakon super().__init__
        instance = getattr(self, 'instance', None)
        initial_data = dict(self.initial) if hasattr(self, 'initial') else {}

        # Odredi company_id iz initial ili iz instance
        company_id = initial_data.get('company')
        if not company_id and instance and instance.pk:
            company_id = instance.company_id

        # Ako je ovo izmena postojećeg ciklusa, popuni inicijalne vrednosti
        if instance and instance.pk:
            # Preselektuj već dodeljene standarde ciklusu
            current_standards_qs = StandardDefinition.objects.filter(
                certification_cycles__certification_cycle=instance
            )
            self.initial['standards'] = list(current_standards_qs.values_list('id', flat=True))

            # Inicijalizuj initial_audit_date iz planiranog datuma ciklusa
            if instance.planirani_datum:
                self.initial['initial_audit_date'] = instance.planirani_datum

            # Pokušaj da dohvatiš lead auditora i broj izveštaja sa inicijalnog audita
            try:
                initial_audit = instance.audits.get(audit_type='initial')
                if initial_audit:
                    if initial_audit.lead_auditor:
                        self.initial['lead_auditor'] = initial_audit.lead_auditor.id
                    if initial_audit.report_number:
                        self.initial['report_number'] = initial_audit.report_number
            except Exception:
                pass

        # Filtriraj opcije standarda:
        # - prikazuj samo standarde koji su dodeljeni kompaniji
        # - isključi one koji su već korišćeni u drugim ciklusima iste kompanije
        # - ali UVEK uključi trenutno odabrane standarde za ovaj ciklus kako bi bili vidljivi prilikom izmene
        if company_id:
            # Svi standardi koje kompanija ima
            company_std_ids = set(
                CompanyStandard.objects.filter(company_id=company_id)
                .values_list('standard_definition_id', flat=True)
            )

            # Standardi korišćeni u drugim ciklusima ove kompanije (ne uključuj trenutni ciklus)
            cycles_qs = CertificationCycle.objects.filter(company_id=company_id)
            if instance and instance.pk:
                cycles_qs = cycles_qs.exclude(id=instance.id)

            used_in_other_cycles = set(
                CycleStandard.objects.filter(certification_cycle__in=cycles_qs)
                .values_list('standard_definition_id', flat=True)
            )

            available_ids = company_std_ids - used_in_other_cycles

            # Dodaj trenutno dodeljene standarde (da budu vidljivi i selektovani)
            if instance and instance.pk:
                current_ids = set(
                    CycleStandard.objects.filter(certification_cycle=instance)
                    .values_list('standard_definition_id', flat=True)
                )
                available_ids |= current_ids

            self.fields['standards'].queryset = (
                StandardDefinition.objects.filter(id__in=available_ids).order_by('code')
            )
        else:
            # Ako nemamo company_id, prikaži makar trenutno dodeljene standarde (za slučaj izmene)
            if instance and instance.pk:
                current_ids = CycleStandard.objects.filter(certification_cycle=instance).values_list('standard_definition_id', flat=True)
                self.fields['standards'].queryset = StandardDefinition.objects.filter(id__in=current_ids).order_by('code')
            else:
                self.fields['standards'].queryset = StandardDefinition.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Dobijamo podatke o inicijalnom auditu iz forme
        initial_audit_date = self.cleaned_data.get('initial_audit_date')
        lead_auditor = self.cleaned_data.get('lead_auditor')
        report_number = self.cleaned_data.get('report_number')
        
        # Ako je postavljen datum planiranog inicijalnog audita, koristimo ga kao planirani datum ciklusa
        if initial_audit_date:
            instance.planirani_datum = initial_audit_date
        else:
            # Ako nema datuma inicijalnog audita, ne možemo nastaviti
            raise forms.ValidationError(_('Datum planiranog inicijalnog audita je obavezan.'))
        
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
                    # Ne postavljamo actual_date niti završavamo audit ovde
                    initial_audit.audit_status = 'planned'
                    
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
            'lead_auditor': forms.Select(attrs={'class': 'form-control', 'id': 'id_lead_auditor'}),
            'report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Sačuvaj request objekat ako je prosleđen
        self.request = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        
        # Uvek prikaži sve auditore u padajućoj listi za lead_auditor
        # (kvalifikacija se proverava u clean())
        self.fields['lead_auditor'].queryset = Auditor.objects.all().order_by('ime_prezime')
        
        # Ako je instanca već kreirana, popunjavamo polje audit_team sa postojećim auditorima
        instance = kwargs.get('instance')
        if instance:
            self.initial['audit_team'] = instance.audit_team.all()
            
            # Onemogući promenu tipa audita za postojeći audit, ali sačuvaj originalnu vrednost
            # Koristimo readonly umesto disabled jer disabled polja ne šalju vrednost u zahtevu
            self.fields['audit_type'].widget.attrs['readonly'] = True
            # Dodatno sakrij polje audit_type da bi bilo nemoguće promeniti ga
            self.fields['audit_type'].widget.attrs['style'] = 'pointer-events: none;'
            
            # Queryset već postavljen globalno; ostavljamo sve auditore dostupne
    
    def clean(self):
        cleaned_data = super().clean()
        lead_auditor = cleaned_data.get('lead_auditor')
        certification_cycle = cleaned_data.get('certification_cycle')
        actual_date = cleaned_data.get('actual_date')
        audit_status = cleaned_data.get('audit_status')
        
        # Onemogući promenu tipa audita nakon kreiranja
        if self.instance.pk:
            original_type = getattr(self.instance, 'audit_type', None)
            new_type = cleaned_data.get('audit_type')
            if new_type and original_type and new_type != original_type:
                self.add_error('audit_type', _('Tip audita nije moguće menjati nakon kreiranja.'))
                cleaned_data['audit_type'] = original_type

        # Automatski postavi status na 'completed' ako je unet stvarni datum (osim kada je status 'cancelled')
        if actual_date:
            if audit_status in ('planned', 'in_progress', 'postponed'):
                cleaned_data['audit_status'] = 'completed'
                # Dodaj informativnu poruku koja će biti prikazana korisniku
                if getattr(self, 'request', None):
                    messages.info(self.request, _('Status audita je automatski postavljen na "Završeno" jer je unet stvarni datum.'))
            elif audit_status == 'cancelled':
                self.add_error('actual_date', _('Za status "Otkazano" ne sme biti postavljen stvarni datum.'))

        # Ako je status 'completed', mora biti postavljen stvarni datum
        if cleaned_data.get('audit_status') == 'completed' and not actual_date:
            self.add_error('actual_date', _('Stvarni datum je obavezan kada je status "Završeno".'))

        # Lead auditor ne može biti i član tima
        team_selected_initial = cleaned_data.get('audit_team')
        if lead_auditor and team_selected_initial and lead_auditor in team_selected_initial:
            self.add_error('audit_team', _('Vodeći auditor ne može biti i član tima.'))
        
        # Proveri da li je lead_auditor kvalifikovan za audit
        if lead_auditor and certification_cycle and self.instance.pk:
            is_qualified, missing_standards = is_auditor_qualified_for_audit(lead_auditor.id, self.instance.pk)
            if not is_qualified:
                missing_codes = ', '.join([std.code for std in missing_standards])
                self.add_error('lead_auditor', _(f'Auditor nije kvalifikovan za standarde: {missing_codes}'))

        # Validacija konflikata rezervacija auditora (spreči duplo zakazivanje)
        # Odredi ciklus, tip audita i osnovni datum za izračun dana audita
        cycle = certification_cycle or getattr(self.instance, 'certification_cycle', None)
        audit_type = cleaned_data.get('audit_type') or getattr(self.instance, 'audit_type', None)
        planned_date = cleaned_data.get('planned_date') or getattr(self.instance, 'planned_date', None)
        base_date = actual_date or planned_date

        # Ako nemamo ciklus ili osnovni datum, ne možemo proveriti konflikt
        if cycle and base_date:
            # Odredi broj dana audita na osnovu ciklusa i tipa
            if audit_type == 'initial' and cycle.inicijalni_broj_dana:
                days_count = zaokruzi_na_veci_broj(cycle.inicijalni_broj_dana)
            elif audit_type in ('surveillance_1', 'surveillance_2') and cycle.broj_dana_nadzora:
                days_count = zaokruzi_na_veci_broj(cycle.broj_dana_nadzora)
            elif audit_type == 'recertification' and cycle.broj_dana_resertifikacije:
                days_count = zaokruzi_na_veci_broj(cycle.broj_dana_resertifikacije)
            else:
                days_count = 1

            # Generiši datume audita (unazad od osnovnog datuma)
            dates = [base_date - timedelta(days=i) for i in range(days_count)]

            # Sakupi sve odabrane auditore (lead + tim)
            team_selected = cleaned_data.get('audit_team') or []
            auditors = set(a.id for a in team_selected)
            if lead_auditor:
                auditors.add(lead_auditor.id)

            if auditors and dates:
                qs = AuditorReservation.objects.filter(auditor_id__in=auditors, date__in=dates)
                if getattr(self.instance, 'pk', None):
                    qs = qs.exclude(audit_id=self.instance.pk)

                conflicts_by_auditor = {}
                for res in qs.select_related('auditor', 'audit', 'audit__certification_cycle__company'):
                    conflicts_by_auditor.setdefault(res.auditor_id, []).append(res)

                if conflicts_by_auditor:
                    # Poruke za lead i tim posebno
                    # Lead auditor
                    if lead_auditor and lead_auditor.id in conflicts_by_auditor:
                        msgs = []
                        for res in conflicts_by_auditor[lead_auditor.id]:
                            company = getattr(res.audit.certification_cycle.company, 'name', '')
                            audit_type_disp = dict(res.audit.AUDIT_TYPE_CHOICES).get(res.audit.audit_type, res.audit.audit_type)
                            msgs.append(f"{res.date.isoformat()} (audit: {company} - {audit_type_disp})")
                        self.add_error(
                            'lead_auditor',
                            _(
                                f'Vodeći auditor {lead_auditor} je već rezervisan za sledeće datume: ' + ', '.join(msgs) +
                                '. Izaberite drugi datum ili auditora.'
                            )
                        )

                    # Tim auditora
                    team_conflicts_msgs = []
                    for auditor_id, res_list in conflicts_by_auditor.items():
                        if lead_auditor and auditor_id == lead_auditor.id:
                            continue
                        # Ovo su članovi tima sa konfliktom
                        auditor_obj = next((a for a in (team_selected or []) if a.id == auditor_id), None)
                        if auditor_obj:
                            parts = []
                            for res in res_list:
                                company = getattr(res.audit.certification_cycle.company, 'name', '')
                                audit_type_disp = dict(res.audit.AUDIT_TYPE_CHOICES).get(res.audit.audit_type, res.audit.audit_type)
                                parts.append(f"{res.date.isoformat()} (audit: {company} - {audit_type_disp})")
                            team_conflicts_msgs.append(f"{auditor_obj} -> " + ', '.join(parts))

                    if team_conflicts_msgs:
                        self.add_error(
                            'audit_team',
                            _(
                                'Sledeći članovi tima su već rezervisani: ' + '; '.join(team_conflicts_msgs) +
                                '. Izaberite drugi datum ili uklonite konfliktne članove.'
                            )
                        )

                    # Globalna greška da sprečimo snimanje
                    raise ValidationError(_('Postoje konflikti rezervacija auditora; proverite označena polja.'))

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

            # Sinhronizuj rezervacije auditora nakon izmene tima/lead auditora
            try:
                instance.sync_auditor_reservations()
            except Exception:
                pass
        
        logger.info("CycleAuditForm.save završena")
        return instance


class SrbijaTimForm(forms.ModelForm):
    """
    Forma za kreiranje i ažuriranje Srbija Tim poseta
    """
    
    class Meta:
        model = SrbijaTim
        fields = [
            'certificate_number',
            'company',
            'standards',
            'certificate_expiry_date',
            'auditors',
            'visit_date',
            'visit_time',
            'broj_dana_posete',
            'status',
            'report_sent',
            'notes'
        ]
        widgets = {
            'certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unesite broj sertifikata'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control select2',
            }),
            'standards': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'certificate_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'auditors': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'visit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'visit_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'broj_dana_posete': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Npr. 1, 1.5, 2'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'report_sent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Dodatne napomene...'
            }),
        }
        labels = {
            'certificate_number': _('Broj sertifikata'),
            'company': _('Kompanija'),
            'standards': _('Standardi'),
            'certificate_expiry_date': _('Datum isticanja sertifikata'),
            'auditors': _('Auditori'),
            'visit_date': _('Datum planiranog sastanka'),
            'visit_time': _('Vreme planiranog sastanka'),
            'broj_dana_posete': _('Broj dana posete'),
            'status': _('Status'),
            'report_sent': _('Poslat izveštaj'),
            'notes': _('Napomene'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Postavi queryset za auditore
        self.fields['auditors'].queryset = Auditor.objects.all().order_by('ime_prezime')
        
        # Postavi queryset za standarde
        self.fields['standards'].queryset = StandardDefinition.objects.all().order_by('code')
        
        # Postavi queryset za kompanije
        self.fields['company'].queryset = Company.objects.all().order_by('name')
        
        # Sva polja su opciona
        for field_name in self.fields:
            self.fields[field_name].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validacija datuma
        visit_date = cleaned_data.get('visit_date')
        certificate_expiry_date = cleaned_data.get('certificate_expiry_date')
        auditors = cleaned_data.get('auditors')
        
        if visit_date and certificate_expiry_date:
            if visit_date > certificate_expiry_date:
                raise forms.ValidationError(
                    'Datum posete ne može biti nakon datuma isticanja sertifikata.'
                )
        
        # Validacija konflikta auditora
        if visit_date and auditors:
            conflicts = []
            for auditor in auditors:
                # Pronađi sve posete ovog auditora na isti datum
                conflicting_visits = SrbijaTim.objects.filter(
                    auditors=auditor,
                    visit_date=visit_date
                )
                
                # Ako je izmena postojeće posete, isključi je iz provere
                if self.instance and self.instance.pk:
                    conflicting_visits = conflicting_visits.exclude(pk=self.instance.pk)
                
                if conflicting_visits.exists():
                    company_names = [v.company.name for v in conflicting_visits]
                    conflicts.append(
                        f"{auditor.ime_prezime} već ima zakazan sastanak tog dana sa: {', '.join(company_names)}"
                    )
            
            if conflicts:
                raise forms.ValidationError({
                    'auditors': 'Konflikt u rasporedu auditora! ' + ' | '.join(conflicts)
                })
        
        return cleaned_data
