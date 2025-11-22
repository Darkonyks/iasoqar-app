import json
import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect

# Konfigurisanje logera
logger = logging.getLogger(__name__)
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings

from .models import Company, Appointment, KontaktOsoba, OstalaLokacija, IAFEACCode, CompanyIAFEACCode
from .standard_models import StandardDefinition, CompanyStandard
from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from datetime import datetime, timedelta
from django.db.models import Count
import random
from .forms import AuditForm, CompanyForm
from .cycle_models import CertificationCycle, CycleStandard, CycleAudit
from .forms import CertificationCycleForm, CycleAuditForm

class CompanyListView(ListView):
    model = Company
    template_name = 'company/company-list.html'
    context_object_name = 'companies'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(pib__icontains=search_query) | 
                Q(mb__icontains=search_query) |
                Q(iaf_eac_codes__iaf_eac_code__iaf_code__icontains=search_query)
            ).distinct()
        
        # Date range filter za istek sertifikata
        expiry_from = self.request.GET.get('expiry_from')
        expiry_to = self.request.GET.get('expiry_to')
        
        if expiry_from:
            try:
                from datetime import datetime
                expiry_from_date = datetime.strptime(expiry_from, '%Y-%m-%d').date()
                # Filtriraj kompanije koje imaju bar jedan standard sa datumom isteka >= expiry_from
                queryset = queryset.filter(
                    company_standards__expiry_date__gte=expiry_from_date
                ).distinct()
            except ValueError:
                pass
        
        if expiry_to:
            try:
                from datetime import datetime
                expiry_to_date = datetime.strptime(expiry_to, '%Y-%m-%d').date()
                # Filtriraj kompanije koje imaju bar jedan standard sa datumom isteka <= expiry_to
                queryset = queryset.filter(
                    company_standards__expiry_date__lte=expiry_to_date
                ).distinct()
            except ValueError:
                pass
        
        # Prefetch related data for better performance
        return queryset.prefetch_related(
            'iaf_eac_codes__iaf_eac_code',
            'company_standards__standard_definition'
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['expiry_from'] = self.request.GET.get('expiry_from', '')
        context['expiry_to'] = self.request.GET.get('expiry_to', '')
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company/company-detail.html'
    context_object_name = 'company'
    
    def get(self, request, *args, **kwargs):
        # Provera da li postoji edit_audit parametar pre pozivanja get_object()
        edit_audit = request.GET.get('edit_audit')
        if edit_audit:
            # Preusmeravanje na stranicu za editovanje audita
            self.object = self.get_object()
            company = self.object
            audit = get_object_or_404(CycleAudit, id=edit_audit, certification_cycle__company=company)
            return redirect('company:cycle_audit_update', pk=audit.id)
        
        # Ako nema edit_audit parametra, nastavljamo normalno sa view-om
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.object
        
        # Get related data
        context['contact_persons'] = company.kontakt_osobe.all().order_by('-is_primary', 'ime_prezime')
        
        # Get standards with their auditors
        standards = company.company_standards.all()
        standards_with_auditors = []
        
        for standard in standards:
            # Ne prikazujemo auditore na nivou standarda kompanije
            # Auditori se dodeljuju na nivou audita u ciklusu, ne na nivou standarda kompanije
            standards_with_auditors.append({
                'standard': standard,
                'auditors': []  # Prazna lista - auditori se dodeljuju na nivou audita
            })
        
        context['standards'] = standards_with_auditors
        context['locations'] = company.ostale_lokacije.all()
        context['appointments'] = company.appointments.all().order_by('-start_datetime')[:5]
        
        # Get IAF/EAC codes for the company
        context['iaf_eac_codes'] = CompanyIAFEACCode.objects.filter(company=company).select_related('iaf_eac_code')
        
        # Get certification cycles for the company
        context['certification_cycles'] = company.certification_cycles.all().order_by('-planirani_datum')
        
        # Get audit information if available
        try:
            context['audit_info'] = company.naredne_provere.first()
        except:
            context['audit_info'] = None
        
        # Check if we need to show cycle or audit form
        add_cycle = self.request.GET.get('add_cycle')
        edit_cycle = self.request.GET.get('edit_cycle')
        
        if add_cycle:
            context['cycle_form'] = CertificationCycleForm(initial={'company': company})
            context['show_cycle_form'] = True
        elif edit_cycle:
            cycle = get_object_or_404(CertificationCycle, id=edit_cycle, company=company)
            context['cycle_form'] = CertificationCycleForm(instance=cycle)
            context['show_cycle_form'] = True
            context['editing_cycle'] = cycle
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        company = self.object
        
        # Handle certification cycle form submission
        if 'submit_cycle_form' in request.POST:
            cycle_id = request.POST.get('cycle_id')
            if cycle_id:
                # Editing existing cycle
                cycle = get_object_or_404(CertificationCycle, id=cycle_id, company=company)
                form = CertificationCycleForm(request.POST, instance=cycle)
            else:
                # Creating new cycle
                form = CertificationCycleForm(request.POST)
            
            if form.is_valid():
                cycle = form.save()
                messages.success(request, 'Ciklus sertifikacije je uspešno sačuvan.')
                return redirect('company:detail', pk=company.id)
            else:
                context = self.get_context_data(**kwargs)
                context['cycle_form'] = form
                context['show_cycle_form'] = True
                if cycle_id:
                    context['editing_cycle'] = get_object_or_404(CertificationCycle, id=cycle_id)
                return render(request, self.template_name, context)
        
        # Handle cycle audit form submission
        elif 'submit_audit_form' in request.POST:
            audit_id = request.POST.get('audit_id')
            if audit_id:
                # Editing existing audit
                audit = get_object_or_404(CycleAudit, id=audit_id, certification_cycle__company=company)
                form = CycleAuditForm(request.POST, instance=audit)
            else:
                # Creating new audit
                form = CycleAuditForm(request.POST)
            
            if form.is_valid():
                audit = form.save()
                messages.success(request, 'Audit je uspešno sačuvan.')
                return redirect('company:detail', pk=company.id)
            else:
                context = self.get_context_data(**kwargs)
                context['audit_form'] = form
                context['show_audit_form'] = True
                if audit_id:
                    context['editing_audit'] = get_object_or_404(CycleAudit, id=audit_id)
                return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)


class CompanyCreateView(CreateView):
    model = Company
    template_name = 'company/company-form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('company:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova kompanija'
        context['submit_text'] = 'Sačuvaj'
        # Dodaj sve IAF/EAC kodove za izbor
        context['all_iaf_eac_codes'] = IAFEACCode.objects.all().order_by('iaf_code')
        # Dodaj sve definicije standarda za izbor
        from .standard_models import StandardDefinition
        context['all_standard_definitions'] = StandardDefinition.objects.filter(active=True).order_by('code')
        return context
    
    def form_valid(self, form):
        # Sačuvaj formu sa commit=True da bi se obradili hidden podaci
        # za standarde i IAF/EAC kodove definisani u CompanyForm.save() metodi
        self.object = form.save(commit=True)
        
        messages.success(self.request, f"Kompanija {form.instance.name} je uspešno kreirana.")
        return HttpResponseRedirect(self.get_success_url())


class CompanyUpdateView(UpdateView):
    model = Company
    template_name = 'company/company-form.html'
    form_class = CompanyForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmena kompanije'
        context['submit_text'] = 'Sačuvaj izmene'
        # Dodaj sve IAF/EAC kodove za izbor
        context['all_iaf_eac_codes'] = IAFEACCode.objects.all().order_by('iaf_code')
        context['iaf_codes'] = IAFEACCode.objects.all().order_by('iaf_code')  # Potrebno za IAF tab
        # Dodaj sve definicije standarda za izbor
        from .standard_models import StandardDefinition
        context['all_standard_definitions'] = StandardDefinition.objects.filter(active=True).order_by('code')
        
        # Dodaj sve auditore za izbor prilikom dodavanja standarda
        context['all_auditors'] = Auditor.objects.all().order_by('ime_prezime')
        
        # Dodaj kontakt osobe za prikaz u kontakt tab-u
        if self.object:
            context['kontakt_osobe'] = self.object.kontakt_osobe.all().order_by('-is_primary', 'ime_prezime')
        return context
    
    def get_success_url(self):
        return reverse_lazy('company:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Sačuvaj formu sa commit=True da bi se obradili hidden podaci
        # za standarde i IAF/EAC kodove definisani u CompanyForm.save() metodi
        self.object = form.save(commit=True)
        
        messages.success(self.request, f"Kompanija {form.instance.name} je uspešno izmenjena.")
        return HttpResponseRedirect(self.get_success_url())


class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'company/company-confirm-delete.html'
    success_url = reverse_lazy('company:list')
    context_object_name = 'company'
    
    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        messages.success(request, f"Kompanija {company.name} je uspešno obrisana.")
        return super().delete(request, *args, **kwargs)


class AuditListView(LoginRequiredMixin, ListView):
    """Pregled svih audita u sistemu"""
    template_name = 'audit/audit-list.html'
    context_object_name = 'audits'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Dohvatamo audite iz CycleAudit i cikluse sertifikacije
        from .cycle_models import CycleAudit, CertificationCycle, CycleStandard
        from .standard_models import StandardDefinition
        
        # Inicijalizujemo praznu listu za sve audite
        combined_audits = []
        
        # Dohvatamo sve cikluse sertifikacije sa standardima
        cycles = CertificationCycle.objects.all().select_related('company').prefetch_related('audits')
        
        # Primenimo filtere na cikluse ako je potrebno
        company_id = self.request.GET.get('company', None)
        if company_id:
            cycles = cycles.filter(company_id=company_id)
        
        # Za svaki ciklus, dohvatimo pripadajuće audite i grupišimo ih
        for cycle in cycles:
            # Dohvatimo sve audite za ovaj ciklus
            cycle_audits = cycle.audits.all().select_related('certification_cycle')
            
            # Primenjujemo status filter ako postoji
            status = self.request.GET.get('status', None)
            if status:
                # Mapiranje starih statusa na nove
                status_mapping = {
                    'active': 'planned',
                    'pending': 'scheduled',  # Ažurirano: in_progress -> scheduled
                    'completed': 'completed',
                    'cancelled': 'cancelled',
                    'postponed': 'postponed'
                }
                mapped_status = status_mapping.get(status, status)
                cycle_audits = cycle_audits.filter(audit_status=mapped_status)
            
            # Primenjujemo datumske filtere
            date_from = self.request.GET.get('date_from', None)
            if date_from:
                cycle_audits = cycle_audits.filter(planned_date__gte=date_from)
                
            date_to = self.request.GET.get('date_to', None)
            if date_to:
                cycle_audits = cycle_audits.filter(planned_date__lte=date_to)
            
            # Ako nema audita nakon filtriranja, preskačemo ovaj ciklus
            if not cycle_audits.exists():
                continue
            
            # Inicijalizujemo podatke za ciklus
            cycle_data = {
                'type': 'new',
                'id': cycle.id,  # Dodajemo ID ciklusa - ovo će nam pomoći kod deduplikacije
                'cycle_id': cycle.id,
                'company': cycle.company,
                'first_surv_due': None,
                'first_surv_cond': None,
                'second_surv_due': None,
                'second_surv_cond': None,
                'trinial_audit_due': None,
                'trinial_audit_cond': None,
                'status': 'active',  # Pretpostavljeni status
                'get_status_display': 'Aktivan',
                'first_audit_id': None,
                'second_audit_id': None,
                'recert_audit_id': None,
                'standards': []
            }
            
            # Dohvatimo standarde za ovaj ciklus
            cycle_standards = CycleStandard.objects.filter(certification_cycle=cycle).select_related('standard_definition')
            cycle_data['standards'] = [cs.standard_definition for cs in cycle_standards]
            
            # Popunjavamo podatke o auditima u okviru ciklusa
            for audit in cycle_audits:
                # Status ciklusa je status najskorijeg audita
                cycle_data['status'] = audit.audit_status
                cycle_data['get_status_display'] = dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status]
                
                # Dodajemo podatke o specifičnom auditu
                if audit.audit_type == 'surveillance_1':
                    cycle_data['first_surv_due'] = audit.planned_date
                    cycle_data['first_surv_cond'] = audit.actual_date
                    cycle_data['first_audit_id'] = audit.id
                elif audit.audit_type == 'surveillance_2':
                    cycle_data['second_surv_due'] = audit.planned_date
                    cycle_data['second_surv_cond'] = audit.actual_date
                    cycle_data['second_audit_id'] = audit.id
                elif audit.audit_type == 'recertification':
                    cycle_data['trinial_audit_due'] = audit.planned_date
                    cycle_data['trinial_audit_cond'] = audit.actual_date
                    cycle_data['recert_audit_id'] = audit.id
            
            # Dodajemo ciklus u listu
            combined_audits.append(cycle_data)
        
        # Ovde jednostavno izostavljamo kod za dodavanje pojedinačnih audita
        # jer to dovodi do dupliranja. Svi auditi će biti prikazani kroz njihov ciklus
        
        # Sortiramo kombinovanu listu po imenu kompanije
        combined_audits.sort(key=lambda x: x['company'].name)
        
        return combined_audits
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add companies for filtering
        context['companies'] = Company.objects.all().order_by('name')
        
        # Add status choices for filtering
        from .cycle_models import CycleAudit
        context['status_choices'] = CycleAudit.AUDIT_STATUS_CHOICES
        
        # Add filter values
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Add today's date for template comparison
        context['today'] = datetime.now()
        
        # Add cycle_audits flag to indicate we're using combined audits
        context['show_cycle_audits'] = True
        
        return context


class CompanyAuditsView(AuditListView):
    template_name = 'audit/company-audits.html'
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Postavljamo company_id iz URL parametra
        self.company_id = kwargs.get('company_id')
        
    def get_queryset(self):
        # Forsiramo filtriranje po kompaniji iz URL-a
        self.request.GET = self.request.GET.copy()
        self.request.GET['company'] = self.company_id
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dodajemo kompaniju u kontekst
        from .models import Company
        context['company'] = Company.objects.get(pk=self.company_id)
        context['is_company_specific'] = True
        return context


class CompanyAuditDetailView(LoginRequiredMixin, DetailView):
    """Pregled detalja audita"""
    template_name = 'audit/audit-detail.html'
    context_object_name = 'audit'
    
    def get_object(self):
        # Sada koristimo samo CycleAudit model
        from .cycle_models import CycleAudit
        return CycleAudit.objects.get(pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audit = self.get_object()
        
        # CycleAudit nema više referencu na calendar_events
        # Calendar eventi se sada dohvataju direktno iz CycleAudit atributa
        
        # Get company details
        context['company'] = audit.certification_cycle.company
        
        # Get company standards
        context['standards'] = audit.certification_cycle.company.company_standards.all()
        
        # Add today's date for template comparison
        context['today'] = datetime.now()
        
        return context


class AuditCreateView(LoginRequiredMixin, CreateView):
    """Kreiranje novog audit zapisa - preusmereno na kreiranje CycleAudit"""
    form_class = AuditForm  # Ažurirati formu kasnije
    template_name = 'audit/audit_form.html'
    
    # Ova klasa je zadržana za kompatibilnost, ali treba preusmeriti na novi sistem audita
    success_url = reverse_lazy('company:audit_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Ako je kompanija već izabrana, filtriramo auditore koji su kvalifikovani za tu kompaniju
        company_id = self.request.GET.get('company', None)
        if company_id:
            try:
                from .audit_utils import get_qualified_auditors_for_company
                
                # Dobijamo rečnik kvalifikovanih auditora po standardima
                qualified_auditors_dict = get_qualified_auditors_for_company(company_id)
                
                # Pronalazimo auditore koji su kvalifikovani za sve standarde kompanije
                if qualified_auditors_dict:
                    # Prvo dobijamo sve standarde koje kompanija ima
                    all_standards = set(qualified_auditors_dict.keys())
                    
                    # Zatim pronalazimo auditore koji su kvalifikovani za sve standarde
                    qualified_auditors = []
                    all_auditors_by_id = {}
                    
                    # Prikupljamo sve auditore iz svih standarda
                    for standard_id, auditors in qualified_auditors_dict.items():
                        for auditor in auditors:
                            if auditor.id not in all_auditors_by_id:
                                all_auditors_by_id[auditor.id] = {
                                    'auditor': auditor,
                                    'standards': set([standard_id])
                                }
                            else:
                                all_auditors_by_id[auditor.id]['standards'].add(standard_id)
                    
                    # Filtriramo samo one koji su kvalifikovani za sve standarde
                    for auditor_id, data in all_auditors_by_id.items():
                        if data['standards'] == all_standards:
                            qualified_auditors.append(data['auditor'])
                    
                    # Ažuriramo queryset za polje auditor
                    if qualified_auditors:
                        form.fields['auditor'].queryset = Auditor.objects.filter(id__in=[a.id for a in qualified_auditors])
                        form.fields['auditor'].help_text = _('Prikazani su samo auditori kvalifikovani za sve standarde kompanije')
            except Exception as e:
                # U slučaju greške, ne filtriramo auditore
                pass
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova nadzorna provera'
        context['submit_text'] = 'Sačuvaj'
        
        # If company_id is provided in GET parameters, pre-select that company
        company_id = self.request.GET.get('company', None)
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                context['preselected_company'] = company
            except Company.DoesNotExist:
                pass
                
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Nadzorna provera za kompaniju {form.instance.company.name} je uspešno kreirana.")
        return super().form_valid(form)


class AuditUpdateView(LoginRequiredMixin, UpdateView):
    """Izmena postojećeg audit zapisa - preusmereno na izmenu CycleAudit"""
    form_class = AuditForm  # Ažurirati formu kasnije
    template_name = 'audit/audit_form.html'
    
    def get_object(self):
        # Sada koristimo samo CycleAudit model
        from .cycle_models import CycleAudit
        return CycleAudit.objects.get(pk=self.kwargs['pk'])
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Dobavljamo trenutnu kompaniju iz instance
        company = self.object.certification_cycle.company
        
        if company:
            try:
                from .audit_utils import get_qualified_auditors_for_company
                
                # Dobijamo rečnik kvalifikovanih auditora po standardima
                qualified_auditors_dict = get_qualified_auditors_for_company(company.id)
                
                # Pronalazimo auditore koji su kvalifikovani za sve standarde kompanije
                if qualified_auditors_dict:
                    # Prvo dobijamo sve standarde koje kompanija ima
                    all_standards = set(qualified_auditors_dict.keys())
                    
                    # Zatim pronalazimo auditore koji su kvalifikovani za sve standarde
                    qualified_auditors = []
                    all_auditors_by_id = {}
                    
                    # Prikupljamo sve auditore iz svih standarda
                    for standard_id, auditors in qualified_auditors_dict.items():
                        for auditor in auditors:
                            if auditor.id not in all_auditors_by_id:
                                all_auditors_by_id[auditor.id] = {
                                    'auditor': auditor,
                                    'standards': set([standard_id])
                                }
                            else:
                                all_auditors_by_id[auditor.id]['standards'].add(standard_id)
                    
                    # Filtriramo samo one koji su kvalifikovani za sve standarde
                    for auditor_id, data in all_auditors_by_id.items():
                        if data['standards'] == all_standards:
                            qualified_auditors.append(data['auditor'])
                    
                    # Dodajemo trenutnog auditora u listu ako postoji
                    current_auditor = self.object.auditor
                    if current_auditor and current_auditor.id not in [a.id for a in qualified_auditors]:
                        qualified_auditors.append(current_auditor)
                    
                    # Ažuriramo queryset za polje auditor
                    if qualified_auditors:
                        form.fields['auditor'].queryset = Auditor.objects.filter(id__in=[a.id for a in qualified_auditors])
                        form.fields['auditor'].help_text = _('Prikazani su samo auditori kvalifikovani za sve standarde kompanije')
            except Exception as e:
                # U slučaju greške, ne filtriramo auditore
                pass
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmena nadzorne provere'
        context['submit_text'] = 'Sačuvaj izmene'
        return context
    
    def get_success_url(self):
        return reverse_lazy('company:audit_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f"Nadzorna provera za kompaniju {form.instance.company.name} je uspešno izmenjena.")
        return super().form_valid(form)


class AuditDeleteView(LoginRequiredMixin, DeleteView):
    """Brisanje audita"""
    template_name = 'audit/audit-confirm-delete.html'
    success_url = reverse_lazy('company:audit_list')
    
    def get_object(self):
        # Sada koristimo samo CycleAudit model
        from .cycle_models import CycleAudit
        return CycleAudit.objects.get(pk=self.kwargs['pk'])
    context_object_name = 'audit'
    
    def delete(self, request, *args, **kwargs):
        audit = self.get_object()
        messages.success(request, f"Nadzorna provera za kompaniju {audit.certification_cycle.company.name} je uspešno obrisana.")
        return super().delete(request, *args, **kwargs)


class CalendarView(TemplateView):  # Privremeno uklonjen LoginRequiredMixin za testiranje
    template_name = 'calendar/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add companies for the appointment form
        context['companies'] = Company.objects.all().order_by('name')
        
        # Dodaj auditore za filter
        from .auditor_models import Auditor
        context['auditors'] = Auditor.objects.all().order_by('ime_prezime')
        
        # Dodaj parametre za početni prikaz kalendara
        context['initial_month'] = self.request.GET.get('month')
        context['initial_year'] = self.request.GET.get('year')
        
        # Dodaj selektovani auditor za filter
        context['selected_auditor'] = self.request.GET.get('auditor', '')

        # Dobij view parametar iz URL-a
        initial_view = self.request.GET.get('view', 'dayGridMonth')
        context['initial_view'] = initial_view
        # Debug log
        print(f"DEBUG CalendarView: month={context['initial_month']}, year={context['initial_year']}, view={context['initial_view']}")
        return context

class CalendarEventsView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar/calendar_events.html'

def dashboard(request):
    # Calculate total companies
    total_companies = Company.objects.count()
    
    # Calculate active companies and certificates
    active_companies = Company.objects.filter(
        certificate_status=Company.STATUS_ACTIVE
    ).count()
    
    # Statistika kompanija po statusu sertifikata
    suspended_companies = Company.objects.filter(
        certificate_status=Company.STATUS_SUSPENDED
    ).count()
    
    expired_companies = Company.objects.filter(
        certificate_status=Company.STATUS_EXPIRED
    ).count()
    
    pending_companies = Company.objects.filter(
        certificate_status=Company.STATUS_PENDING
    ).count()
    
    withdrawn_companies = Company.objects.filter(
        certificate_status=Company.STATUS_WITHDRAWN
    ).count()
    
    cancelled_companies = Company.objects.filter(
        certificate_status=Company.STATUS_CANCELLED
    ).count()
    
    # Importi za modele
    from .standard_models import CompanyStandard
    from .cycle_models import CycleAudit
    from .srbija_tim_models import SrbijaTim
    from .auditor_models import Auditor
    from .cycle_models import AuditorReservation, CertificationCycle
    
    # Count active certificates (standards associated with active companies)
    active_certificates = CompanyStandard.objects.filter(
        company__certificate_status=Company.STATUS_ACTIVE
    ).count()
    
    # Calculate expired certificates (zadržano zbog kompatibilnosti)
    expired_certificates = expired_companies
    
    # Get audits scheduled for the current work week
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    next_month = today + timedelta(days=30)  # Definisanje sledećeg meseca za upite
    
    # Auditi - Pregled Statusa
    
    # Planirani auditi
    planned_audits_count = CycleAudit.objects.filter(audit_status='planned').count()
    
    # Zakazani auditi
    scheduled_audits_count = CycleAudit.objects.filter(audit_status='scheduled').count()
    
    # Završeni auditi (ovaj mesec)
    current_month_start = today.replace(day=1)
    if today.month == 12:
        next_month_start = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month_start = today.replace(month=today.month + 1, day=1)
    
    completed_audits_this_month = CycleAudit.objects.filter(
        audit_status='completed',
        actual_date__gte=current_month_start,
        actual_date__lt=next_month_start
    ).count()
    
    # Odloženi auditi
    postponed_audits_count = CycleAudit.objects.filter(audit_status='postponed').count()
    
    # Auditi u narednih 30 dana
    thirty_days_from_now = today + timedelta(days=30)
    upcoming_audits_30_days = CycleAudit.objects.filter(
        planned_date__gte=today,
        planned_date__lte=thirty_days_from_now
    ).exclude(
        audit_status='cancelled'
    ).order_by('planned_date').select_related(
        'certification_cycle__company',
        'lead_auditor'
    )
    
    # Prosečan broj dana po auditu (iz ciklusa)
    from django.db.models import Avg
    from .cycle_models import CertificationCycle
    
    avg_audit_days = CertificationCycle.objects.filter(
        status='active'
    ).aggregate(
        avg_initial=Avg('inicijalni_broj_dana'),
        avg_surveillance=Avg('broj_dana_nadzora'),
        avg_recert=Avg('broj_dana_resertifikacije')
    )
    
    # Izračunaj ukupan prosek (ako postoje vrednosti)
    total_avg_days = 0
    count_avg = 0
    if avg_audit_days['avg_initial']:
        total_avg_days += float(avg_audit_days['avg_initial'])
        count_avg += 1
    if avg_audit_days['avg_surveillance']:
        total_avg_days += float(avg_audit_days['avg_surveillance'])
        count_avg += 1
    if avg_audit_days['avg_recert']:
        total_avg_days += float(avg_audit_days['avg_recert'])
        count_avg += 1
    
    average_audit_days = round(total_avg_days / count_avg, 1) if count_avg > 0 else 0
    
    # Srbija Tim - Crni Kalendar Statistika
    # Zakazane posete (ovaj mesec)
    srbija_tim_scheduled_this_month = SrbijaTim.objects.filter(
        status='zakazan',
        visit_date__gte=current_month_start,
        visit_date__lt=next_month_start
    ).count()
    
    # Odrađene posete (ovaj mesec)
    srbija_tim_completed_this_month = SrbijaTim.objects.filter(
        status='odradjena',
        visit_date__gte=current_month_start,
        visit_date__lt=next_month_start
    ).count()
    
    # Poslati izveštaji
    srbija_tim_reports_sent = SrbijaTim.objects.filter(
        report_sent=True
    ).count()
    
    # Neposlati izveštaji (odrađene posete bez izveštaja)
    srbija_tim_reports_pending = SrbijaTim.objects.filter(
        status='odradjena',
        report_sent=False
    ).count()
    
    # Posete u narednih 7 dana
    seven_days_from_now = today + timedelta(days=7)
    srbija_tim_upcoming_7_days = SrbijaTim.objects.filter(
        visit_date__gte=today,
        visit_date__lte=seven_days_from_now
    ).order_by('visit_date').select_related('company').prefetch_related('auditors', 'standards')
    
    # Sertifikati - Isticanje
    # Sertifikati koji ističu u narednih 30 dana
    expiring_30_days = CompanyStandard.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=30)
    ).select_related('company', 'standard_definition').count()
    
    # Sertifikati koji ističu u narednih 60 dana
    expiring_60_days = CompanyStandard.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=60)
    ).select_related('company', 'standard_definition').count()
    
    # Sertifikati koji ističu u narednih 90 dana
    expiring_90_days = CompanyStandard.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=90)
    ).select_related('company', 'standard_definition').count()
    
    # Već istekli sertifikati
    expired_certificates_count = CompanyStandard.objects.filter(
        expiry_date__lt=today
    ).count()
    
    # Lista sertifikata koji ističu u narednih 30 dana (za tabelu)
    expiring_certificates_list = CompanyStandard.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=30)
    ).select_related('company', 'standard_definition').order_by('expiry_date')[:10]
    
    # Auditori - Zauzetost
    # Ukupan broj auditora
    total_auditors = Auditor.objects.count()
    
    # Najzauzetiji auditor (ovaj mesec) - broj rezervacija
    from django.db.models import Count
    busiest_auditor = AuditorReservation.objects.filter(
        date__gte=current_month_start,
        date__lt=next_month_start
    ).values('auditor__ime_prezime').annotate(
        reservation_count=Count('id')
    ).order_by('-reservation_count').first()
    
    # Dostupni auditori (danas) - auditori bez rezervacija
    reserved_auditor_ids = AuditorReservation.objects.filter(
        date=today
    ).values_list('auditor_id', flat=True).distinct()
    
    available_auditors_today = Auditor.objects.exclude(
        id__in=reserved_auditor_ids
    ).count()
    
    # Aktivni ciklusi
    active_cycles = CertificationCycle.objects.filter(status='active').count()
    
    # Završeni ciklusi (ova godina)
    year_start = today.replace(month=1, day=1)
    completed_cycles_this_year = CertificationCycle.objects.filter(
        status='completed',
        updated_at__gte=year_start
    ).count()
    
    # Integrisani sistemi
    integrated_systems = CertificationCycle.objects.filter(
        is_integrated_system=True,
        status='active'
    ).count()
    
    # Get planned audits for this week
    this_week_audits = []
    upcoming_audits = CycleAudit.objects.filter(
        Q(planned_date__gt=today) & 
        Q(planned_date__lt=next_month) &
        Q(audit_status='planned')
    ).order_by('planned_date').select_related('certification_cycle__company')
    
    # Organizovano po tipu audita
    first_audits = upcoming_audits.filter(audit_type='surveillance_1')
    second_audits = upcoming_audits.filter(audit_type='surveillance_2')
    recert_audits = upcoming_audits.filter(audit_type='recertification')
    
    for audit in first_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.certification_cycle.company.name,
            'type': 'Prva nadzorna provera',
            'date': audit.planned_date,
            'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status]
        })
    
    for audit in second_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.certification_cycle.company.name,
            'type': 'Druga nadzorna provera',
            'date': audit.planned_date,
            'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status]
        })
    
    for audit in recert_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.certification_cycle.company.name,
            'type': 'Resertifikacija',
            'date': audit.planned_date,
            'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status]
        })
    
    # Sort audits by date
    this_week_audits.sort(key=lambda x: x['date'])
    
    # Get standards distribution
    standards_distribution = CompanyStandard.objects.values('standard_definition__standard').annotate(
        total=Count('standard_definition')
    ).order_by('-total')
    
    # Prepare chart data
    standards_labels = [item['standard_definition__standard'] for item in standards_distribution]
    standards_data = [item['total'] for item in standards_distribution]
    
    # Get all companies for the list
    companies = Company.objects.all().order_by('name')
    
    # Calculate certificate status distribution
    certificate_status = Company.objects.values('certificate_status').annotate(
        total=Count('certificate_status')
    )
    
    # Prepare certificate chart data
    certificate_labels = [str(dict(Company.CERTIFICATE_STATUS_CHOICES).get(status['certificate_status']))
                        for status in certificate_status]
    certificate_data = [status['total'] for status in certificate_status]

    # Statistika za audite po statusu - sad koristimo novi model
    from .cycle_models import CycleAudit
    
    audit_status = CycleAudit.objects.values('audit_status').annotate(
        count=Count('audit_status')
    ).order_by('audit_status')
    
    # Pripremamo labele i podatke za chart
    audit_labels = [str(dict(CycleAudit.AUDIT_STATUS_CHOICES).get(status['audit_status'], 'Nepoznato')) 
                   for status in audit_status]
    audit_data = [status['count'] for status in audit_status]
    
    # Prepare standards distribution for pie chart
    standards_distribution = CompanyStandard.objects.values('standard_definition__standard').annotate(
        total=Count('standard_definition')
    ).order_by('-total')
    
    # Handle null standards and format for Chart.js
    standards_labels = [item['standard_definition__standard'] or 'No Standard' for item in standards_distribution]
    standards_data = [item['total'] for item in standards_distribution]
    
    # Generate random colors for each standard
    standards_colors = [
        f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.7)"
        for _ in standards_labels
    ]
    
    # Debug logging
    print("Standards Distribution Data:")
    print(list(zip(standards_labels, standards_data)))
    
    print("Certificate Status Data:")
    print("Labels:", certificate_labels)
    print("Data:", certificate_data)
    
    print("Audit Status Data:")
    print("Labels:", audit_labels)
    print("Data:", audit_data)
    
    context = {
        'total_companies': total_companies,
        'active_companies': active_companies,
        'suspended_companies': suspended_companies,
        'expired_companies': expired_companies,
        'pending_companies': pending_companies,
        'withdrawn_companies': withdrawn_companies,
        'cancelled_companies': cancelled_companies,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
        # Auditi statistika
        'planned_audits_count': planned_audits_count,
        'scheduled_audits_count': scheduled_audits_count,
        'completed_audits_this_month': completed_audits_this_month,
        'postponed_audits_count': postponed_audits_count,
        'upcoming_audits_30_days': upcoming_audits_30_days,
        'upcoming_audits_30_days_count': upcoming_audits_30_days.count(),
        'average_audit_days': average_audit_days,
        # Srbija Tim statistika
        'srbija_tim_scheduled_this_month': srbija_tim_scheduled_this_month,
        'srbija_tim_completed_this_month': srbija_tim_completed_this_month,
        'srbija_tim_reports_sent': srbija_tim_reports_sent,
        'srbija_tim_reports_pending': srbija_tim_reports_pending,
        'srbija_tim_upcoming_7_days': srbija_tim_upcoming_7_days,
        'srbija_tim_upcoming_7_days_count': srbija_tim_upcoming_7_days.count(),
        # Sertifikati - Isticanje
        'expiring_30_days': expiring_30_days,
        'expiring_60_days': expiring_60_days,
        'expiring_90_days': expiring_90_days,
        'expired_certificates_count': expired_certificates_count,
        'expiring_certificates_list': expiring_certificates_list,
        # Auditori
        'total_auditors': total_auditors,
        'busiest_auditor': busiest_auditor,
        'available_auditors_today': available_auditors_today,
        # Ciklusi
        'active_cycles': active_cycles,
        'completed_cycles_this_year': completed_cycles_this_year,
        'integrated_systems': integrated_systems,
        # Datumi za badge-ove
        'today': today,
        'seven_days_from_now': seven_days_from_now,
        'companies': companies,
        'standards_labels': json.dumps(standards_labels),
        'standards_data': json.dumps(standards_data),
        'certificate_labels': json.dumps(certificate_labels),
        'certificate_data': json.dumps(certificate_data),
        'standards_distribution_labels': json.dumps(standards_labels),
        'standards_distribution_data': json.dumps(standards_data),
        'audit_status_labels': json.dumps(audit_labels),
        'audit_status_data': json.dumps(audit_data),
        'this_week_audits': this_week_audits,
    }
    
    return render(request, 'dashboard.html', context)

def audit_detail_json(request, pk):
    """API endpoint za dobijanje detalja audita u JSON formatu"""
    import logging
    from .cycle_models import CycleAudit, AuditDay
    
    logger = logging.getLogger(__name__)
    logger.info(f"Pristup audit_detail_json za audit ID: {pk}")
    
    try:
        # Dohvatanje audita sa svim povezanim podacima
        logger.debug(f"Dohvatanje audita sa ID: {pk}")
        audit = CycleAudit.objects.select_related('certification_cycle__company').get(pk=pk)
        logger.debug(f"Audit pronađen: {audit}")
        
        # Kreiranje osnovnog JSON odgovora
        data = {
            'id': audit.id,
            'audit_type': audit.audit_type,
            'audit_status': audit.audit_status,
            'notes': audit.notes or ''
        }
        
        # Sigurno dodavanje podataka o kompaniji
        try:
            if audit.certification_cycle and audit.certification_cycle.company:
                data['company'] = {
                    'id': audit.certification_cycle.company.id,
                    'name': audit.certification_cycle.company.name
                }
            else:
                data['company'] = {'id': None, 'name': 'Nepoznata kompanija'}
        except Exception as e:
            logger.error(f"Greška prilikom dohvatanja podataka o kompaniji: {str(e)}")
            data['company'] = {'id': None, 'name': 'Greška pri dohvatanju'}
        
        # Sigurno dodavanje podataka o certifikacionom ciklusu
        try:
            if audit.certification_cycle:
                cycle_data = {
                    'id': audit.certification_cycle.id,
                    'status': audit.certification_cycle.status
                }

                # Sigurno formatiranje datuma ciklusa (planirani_datum)
                try:
                    if audit.certification_cycle.planirani_datum:
                        cycle_data['planirani_datum'] = audit.certification_cycle.planirani_datum.isoformat()
                    else:
                        cycle_data['planirani_datum'] = None
                except Exception as e:
                    logger.error(f"Greška sa planirani_datum: {str(e)}")
                    cycle_data['planirani_datum'] = None
                    
                data['certification_cycle'] = cycle_data
            else:
                data['certification_cycle'] = {'id': None, 'status': 'Nepoznat'}
        except Exception as e:
            logger.error(f"Greška prilikom dohvatanja podataka o ciklusu: {str(e)}")
            data['certification_cycle'] = {'id': None, 'status': 'Greška pri dohvatanju'}
        
        # Sigurno dodavanje display vrednosti
        try:
            data['audit_type_display'] = dict(audit.AUDIT_TYPE_CHOICES).get(audit.audit_type, 'Nepoznat')
            data['audit_status_display'] = dict(audit.AUDIT_STATUS_CHOICES).get(audit.audit_status, 'Nepoznat')
        except Exception as e:
            logger.error(f"Greška prilikom dohvatanja display vrednosti: {str(e)}")
            data['audit_type_display'] = 'Greška pri dohvatanju'
            data['audit_status_display'] = 'Greška pri dohvatanju'
        
        # Sigurno formatiranje datuma audita
        try:
            data['planned_date'] = audit.planned_date.isoformat() if audit.planned_date else None
        except Exception as e:
            logger.error(f"Greška sa planned_date: {str(e)}")
            data['planned_date'] = None
            
        try:
            data['actual_date'] = audit.actual_date.isoformat() if audit.actual_date else None
        except Exception as e:
            logger.error(f"Greška sa actual_date: {str(e)}")
            data['actual_date'] = None
        
        # Sigurno dohvatanje broja dana audita
        try:
            data['audit_days_count'] = audit.get_audit_days_count()
        except Exception as e:
            logger.error(f"Greška prilikom dohvatanja broja dana audita: {str(e)}")
            data['audit_days_count'] = 0
        
        # Sigurno dohvatanje dana audita
        try:
            audit_days = AuditDay.objects.filter(audit=audit).order_by('date')
            logger.debug(f"Broj dana audita: {audit_days.count()}")
            
            days_data = []
            for day in audit_days:
                try:
                    day_data = {
                        'id': day.id,
                        'is_planned': day.is_planned,
                        'is_actual': day.is_actual,
                        'notes': day.notes or ''
                    }
                    
                    # Sigurno formatiranje datuma dana audita
                    try:
                        if day.date:
                            day_data['date'] = day.date.isoformat()
                        else:
                            day_data['date'] = None
                    except Exception as e:
                        logger.error(f"Greška sa formatiranjem datuma dana audita: {str(e)}")
                        day_data['date'] = None
                        
                    days_data.append(day_data)
                except Exception as e:
                    logger.error(f"Greška prilikom obrade dana audita {day.id}: {str(e)}")
            
            data['audit_days'] = days_data
        except Exception as e:
            logger.error(f"Greška prilikom dohvatanja dana audita: {str(e)}")
            data['audit_days'] = []
        
        logger.debug("JSON odgovor kreiran uspešno")
        return JsonResponse(data)
    except CycleAudit.DoesNotExist:
        logger.warning(f"Audit sa ID {pk} nije pronađen")
        return JsonResponse({'error': 'Audit nije pronađen'}, status=404)
    except Exception as e:
        import traceback
        logger.error(f"Greška prilikom dohvatanja audita {pk}: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def appointment_calendar_json(request):
    """API endpoint for getting appointment data in FullCalendar format"""
    # Get filter parametar za auditora
    auditor_id = request.GET.get('auditor')
    
    logger.info(f"Calendar JSON request - auditor filter: {auditor_id}")
    
    # Get all appointments
    appointments = Appointment.objects.all()
    logger.info(f"Total appointments before filter: {appointments.count()}")
    
    # Napomena: Appointment model trenutno nema 'auditors' polje
    # Ovaj filter neće raditi dok se ne doda to polje u model
    # if auditor_id:
    #     appointments = appointments.filter(auditors__id=auditor_id)
    
    # Za sada, ako je auditor selektovan, ne prikazuj Appointment objekte
    # jer ne možemo da ih filtriramo
    if auditor_id:
        appointments = appointments.none()
    
    events = []
    
    # Add appointments to events
    for appointment in appointments:
        # Pokušaj da povežeš termin sa Danom audita istog klijenta na isti lokalni datum
        try:
            from django.utils import timezone as dj_tz
            appt_dt = appointment.start_datetime
            if dj_tz.is_naive(appt_dt):
                appt_dt = dj_tz.make_aware(appt_dt, dj_tz.get_current_timezone())
            local_date = dj_tz.localtime(appt_dt, dj_tz.get_current_timezone()).date()
            # Lokalni import da izbegnemo cirkularne zavisnosti pri uvozu modula
            from .cycle_models import AuditDay as _AuditDay
            related_day = _AuditDay.objects.filter(
                audit__certification_cycle__company=appointment.company,
                date=local_date
            ).select_related('audit').first()
        except Exception:
            related_day = None

        events.append({
            'id': appointment.id,
            'title': appointment.title,
            'start': appointment.start_datetime.isoformat(),
            'end': appointment.end_datetime.isoformat() if appointment.end_datetime else None,
            'allDay': appointment.all_day,
            'color': appointment.get_status_color(),
            'url': f'/company/appointments/{appointment.id}/',
            'extendedProps': {
                'company': appointment.company.name,
                'type': appointment.get_appointment_type_display(),
                'status': appointment.get_status_display(),
                'location': appointment.location or ('Online' if appointment.is_online else 'N/A'),
                'eventType': 'appointment',
                'appointment_id': appointment.id,
                # Link ka Danu audita ako postoji na isti datum
                'related_audit_day_id': related_day.id if related_day else None,
                'related_audit_id': related_day.audit_id if related_day else None,
                'related_is_planned': related_day.is_planned if related_day else None,
                'related_is_actual': related_day.is_actual if related_day else None,
            }
        })
    
    # Stari model NaredneProvere je uklonjen - sada se koristi samo novi model CycleAudit
    
    # Get all audit dates from the new model (CycleAudit)
    from .cycle_models import CycleAudit, AuditDay
    from django.db.models import Q
    
    cycle_audits = CycleAudit.objects.all().select_related('certification_cycle__company')
    
    # Filtriraj CycleAudit po auditoru ako je selektovan
    # Auditor može biti vodeći auditor ili član tima
    if auditor_id:
        cycle_audits = cycle_audits.filter(
            Q(lead_auditor__id=auditor_id) | Q(audit_team__id=auditor_id)
        ).distinct()
        logger.info(f"Filtered CycleAudits count: {cycle_audits.count()}")
    
    audit_type_mapping = {
        'surveillance_1': {
            'name': 'Prva nadzorna provera',
            'color_planned': '#FF9800',      # Narandžasta - planirano
            'color_scheduled': '#F44336',    # Crvena - zakazano
            'color_postponed': '#9E9E9E',    # Siva - odloženo
            'color_completed': '#4CAF50',    # Zelena - završeno
            'color_cancelled': '#424242'     # Tamno siva - otkazano
        },
        'surveillance_2': {
            'name': 'Druga nadzorna provera',
            'color_planned': '#FF9800',      # Narandžasta - planirano
            'color_scheduled': '#F44336',    # Crvena - zakazano
            'color_postponed': '#9E9E9E',    # Siva - odloženo
            'color_completed': '#4CAF50',    # Zelena - završeno
            'color_cancelled': '#424242'     # Tamno siva - otkazano
        },
        'recertification': {
            'name': 'Resertifikacija',
            'color_planned': '#E91E63',      # Roza - planirano
            'color_scheduled': '#F44336',    # Crvena - zakazano
            'color_postponed': '#9E9E9E',    # Siva - odloženo
            'color_completed': '#4CAF50',    # Zelena - završeno
            'color_cancelled': '#424242'     # Tamno siva - otkazano
        },
        'initial': {
            'name': 'Inicijalni audit',
            'color_planned': '#3788d8',      # Plava - planirano
            'color_scheduled': '#F44336',    # Crvena - zakazano
            'color_postponed': '#9E9E9E',    # Siva - odloženo
            'color_completed': '#4CAF50',    # Zelena - završeno
            'color_cancelled': '#424242'     # Tamno siva - otkazano
        }
    }
    
    # Get all audit days - prikazuj sve dane bez obzira na status audita
    # Boja će se odrediti na osnovu statusa audita
    audit_days = (
        AuditDay.objects
        .select_related('audit__certification_cycle__company', 'audit__lead_auditor')
        .prefetch_related('audit__audit_team')
    )
    
    # Filtriraj AuditDay po auditoru ako je selektovan
    if auditor_id:
        audit_days = audit_days.filter(
            Q(audit__lead_auditor__id=auditor_id) | Q(audit__audit_team__id=auditor_id)
        ).distinct()
        logger.info(f"Filtered AuditDays count: {audit_days.count()}")
    
    # Add audit days to events
    for audit_day in audit_days:
        audit = audit_day.audit
        company_name = audit.certification_cycle.company.name
        audit_type_info = audit_type_mapping.get(audit.audit_type, {})
        audit_name = audit_type_info.get('name', 'Audit')
        
        # Determine if this is a planned or actual day
        is_planned = audit_day.is_planned
        is_actual = audit_day.is_actual
        
        # Preferiramo "stvarni" dan nad "planiranim" ako su oba označena
        if is_actual:
            # Ako je isti datum kao glavni actual_date ciklusa, preskoči (da ne dupliramo cycle event)
            if audit.actual_date and audit_day.date == audit.actual_date:
                pass
            else:
                # Određuj boju na osnovu statusa audita
                if audit.audit_status == 'completed':
                    color = audit_type_info.get('color_completed', '#4CAF50')
                    status_text = 'završen'
                elif audit.audit_status == 'scheduled':
                    color = audit_type_info.get('color_scheduled', '#F44336')
                    status_text = 'zakazan'
                elif audit.audit_status == 'postponed':
                    color = audit_type_info.get('color_postponed', '#9E9E9E')
                    status_text = 'odložen'
                elif audit.audit_status == 'cancelled':
                    color = audit_type_info.get('color_cancelled', '#424242')
                    status_text = 'otkazan'
                else:  # planned
                    color = audit_type_info.get('color_planned', '#3788d8')
                    status_text = 'planiran'
                
                # Override boju ako je poslat izveštaj - tamno zelena
                if audit.poslat_izvestaj:
                    color = '#1B5E20'  # Tamno zelena
                
                # Add actual audit day
                events.append({
                'id': f'audit_day_actual_{audit_day.id}',
                'title': f'{company_name} - {audit_name} ({status_text})',
                'start': audit_day.date.isoformat(),
                'allDay': True,
                'color': color,
                # Uklonjen URL da bi se omogućilo otvaranje modala
                # 'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': f'{audit_name} - Dan audita',
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES).get(audit.audit_status, 'Održano'),
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'audit_day',
                    'auditStatus': 'completed' if audit.audit_status == 'completed' else 'actual',
                    'modelType': 'audit_day',
                    'audit_id': audit.id,  # Dodato za povezivanje sa modalnim prozorom
                    'audit_day_id': audit_day.id,
                    'notes': audit_day.notes or audit.notes or 'N/A'
                }
            })
        elif is_planned:
            # Ako je isti datum kao glavni planned_date ciklusa, preskoči (da ne dupliramo cycle event)
            if audit.planned_date and audit_day.date == audit.planned_date:
                pass
            else:
                # Određuj boju na osnovu statusa audita
                if audit.audit_status == 'completed':
                    color = audit_type_info.get('color_completed', '#4CAF50')
                    status_text = 'završen'
                elif audit.audit_status == 'scheduled':
                    color = audit_type_info.get('color_scheduled', '#F44336')
                    status_text = 'zakazan'
                elif audit.audit_status == 'postponed':
                    color = audit_type_info.get('color_postponed', '#9E9E9E')
                    status_text = 'odložen'
                elif audit.audit_status == 'cancelled':
                    color = audit_type_info.get('color_cancelled', '#424242')
                    status_text = 'otkazan'
                else:  # planned
                    color = audit_type_info.get('color_planned', '#3788d8')
                    status_text = 'planiran'
                
                # Override boju ako je poslat izveštaj - tamno zelena
                if audit.poslat_izvestaj:
                    color = '#1B5E20'  # Tamno zelena
                
                # Add planned audit day
                events.append({
                'id': f'audit_day_planned_{audit_day.id}',
                'title': f'{company_name} - {audit_name} ({status_text})',
                'start': audit_day.date.isoformat(),
                'allDay': True,
                'color': color,
                # Uklonjen URL da bi se omogućilo otvaranje modala
                # 'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': f'{audit_name} - Dan audita',
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES).get(audit.audit_status, 'Planirano'),
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'audit_day',
                    'auditStatus': 'completed' if audit.audit_status == 'completed' else 'planned',
                    'modelType': 'audit_day',
                    'audit_id': audit.id,  # Dodato za povezivanje sa modalnim prozorom
                    'audit_day_id': audit_day.id,
                    'notes': audit_day.notes or audit.notes or 'N/A'
                }
            })
    
    # Add cycle audit dates to events (glavni audit datumi)
    for audit in cycle_audits:
        # Get company name from certification cycle
        company_name = audit.certification_cycle.company.name
        audit_type_info = audit_type_mapping.get(audit.audit_type, {})
        audit_name = audit_type_info.get('name', 'Audit')
        
        # Determine audit status and color
        is_completed = audit.audit_status in ['completed']
        
        # Određuj boju na osnovu statusa audita
        dark_green = '#1B5E20'  # Tamno zelena za poslat izveštaj
        
        if audit.audit_status == 'completed':
            base_color = audit_type_info.get('color_completed', '#4CAF50')
        elif audit.audit_status == 'scheduled':
            base_color = audit_type_info.get('color_scheduled', '#F44336')
        elif audit.audit_status == 'postponed':
            base_color = audit_type_info.get('color_postponed', '#9E9E9E')
        elif audit.audit_status == 'cancelled':
            base_color = audit_type_info.get('color_cancelled', '#424242')
        else:  # planned
            base_color = audit_type_info.get('color_planned', '#3788d8')
        
        # Override boju ako je poslat izveštaj
        planned_color = dark_green if audit.poslat_izvestaj else base_color
        actual_color = dark_green if audit.poslat_izvestaj else base_color
        
        # Određuj status tekst za naslov
        if audit.audit_status == 'completed':
            status_text = 'završen'
        elif audit.audit_status == 'scheduled':
            status_text = 'zakazan'
        elif audit.audit_status == 'postponed':
            status_text = 'odložen'
        elif audit.audit_status == 'cancelled':
            status_text = 'otkazan'
        else:  # planned
            status_text = 'planiran'

        # Izbegni dupliranje: ako postoje AuditDay zapisi za isti datum, ne prikazuj glavni audit događaj
        try:
            has_planned_day = bool(audit.planned_date) and audit.audit_days.filter(is_planned=True, date=audit.planned_date).exists()
        except Exception:
            has_planned_day = False
        try:
            has_actual_day = bool(audit.actual_date) and audit.audit_days.filter(is_actual=True, date=audit.actual_date).exists()
        except Exception:
            has_actual_day = False
        
        # Add planned audit only if not completed with an actual date
        # Ako je audit završen i postoji stvarni datum, ne prikazuj planirani događaj
        if audit.planned_date and not (is_completed and audit.actual_date):
            events.append({
                'id': f'cycle_audit_planned_{audit.id}',
                'title': f'{audit_name} - {company_name} ({status_text})',
                'start': audit.planned_date.isoformat(),
                'allDay': True,
                'color': planned_color,
                # Uklonjen URL da bi se omogućilo otvaranje modala
                # 'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': audit_name,
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'cycle_audit',
                    'auditStatus': 'planned' if not is_completed else 'completed',
                    'modelType': 'new',
                    'audit_id': audit.id,
                    'notes': audit.notes or 'N/A',
                    'poslat_izvestaj': audit.poslat_izvestaj,
                }
            })
        
        # Add completed audit uvek (dozvoli prikaz glavnog termina)
        if audit.actual_date:
            events.append({
                'id': f'cycle_audit_actual_{audit.id}',
                'title': f'{company_name} - {audit_name} ({status_text})',
                'start': audit.actual_date.isoformat(),
                'allDay': True,
                'color': actual_color,
                # Uklonjen URL da bi se omogućilo otvaranje modala
                # 'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': audit_name,
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'cycle_audit',
                    'auditStatus': 'completed',
                    'modelType': 'new',
                    'audit_id': audit.id,
                    'notes': audit.notes or 'N/A',
                    'poslat_izvestaj': audit.poslat_izvestaj,
                }
            })
    
    logger.info(f"Total events returned: {len(events)}")
    logger.info(f"Events summary - Appointments: {len([e for e in events if e.get('extendedProps', {}).get('eventType') == 'appointment'])}, Audit days: {len([e for e in events if e.get('extendedProps', {}).get('eventType') == 'audit_day'])}, Cycle audits: {len([e for e in events if e.get('extendedProps', {}).get('eventType') == 'cycle_audit'])}")
    return JsonResponse(events, safe=False)

def appointment_detail(request, pk):
    """View for appointment details"""
    appointment = Appointment.objects.get(pk=pk)
    context = {
        'appointment': appointment,
        'contact_persons': appointment.contact_persons.all(),
    }
    return render(request, 'calendar/appointment_detail.html', context)

def appointment_create(request):
    """View for creating appointments"""
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        company_id = request.POST.get('company')
        appointment_type = request.POST.get('appointment_type')
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        all_day = request.POST.get('all_day', False) == 'on'
        location = request.POST.get('location')
        is_online = request.POST.get('is_online', False) == 'on'
        meeting_link = request.POST.get('meeting_link')
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        contact_persons = request.POST.getlist('contact_persons')
        external_attendees = request.POST.get('external_attendees')
        
        # Create appointment
        appointment = Appointment.objects.create(
            title=title,
            company_id=company_id,
            appointment_type=appointment_type,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            all_day=all_day,
            location=location,
            is_online=is_online,
            meeting_link=meeting_link,
            status=status,
            notes=notes,
            external_attendees=external_attendees
        )
        
        # Add contact persons
        if contact_persons:
            appointment.contact_persons.set(contact_persons)
        
        return JsonResponse({'status': 'success', 'id': appointment.id})
    
    # GET request - return form data
    companies = Company.objects.all().order_by('name')
    context = {
        'companies': companies,
        'appointment_types': Appointment.APPOINTMENT_TYPE_CHOICES,
        'status_choices': Appointment.APPOINTMENT_STATUS_CHOICES,
    }
    return render(request, 'calendar/appointment_form.html', context)

def appointment_update(request, pk):
    """View for updating appointments"""
    appointment = Appointment.objects.get(pk=pk)
    
    if request.method == 'POST':
        # Process form data
        appointment.title = request.POST.get('title')
        appointment.company_id = request.POST.get('company')
        appointment.appointment_type = request.POST.get('appointment_type')
        appointment.start_datetime = request.POST.get('start_datetime')
        appointment.end_datetime = request.POST.get('end_datetime')
        appointment.all_day = request.POST.get('all_day', False) == 'on'
        appointment.location = request.POST.get('location')
        appointment.is_online = request.POST.get('is_online', False) == 'on'
        appointment.meeting_link = request.POST.get('meeting_link')
        appointment.status = request.POST.get('status')
        appointment.notes = request.POST.get('notes')
        appointment.external_attendees = request.POST.get('external_attendees')
        
        # Update appointment
        appointment.save()
        
        # Update contact persons
        contact_persons = request.POST.getlist('contact_persons')
        if contact_persons:
            appointment.contact_persons.set(contact_persons)
        else:
            appointment.contact_persons.clear()
        
        return JsonResponse({'status': 'success'})
    
    # GET request - return form with appointment data
    companies = Company.objects.all().order_by('name')
    contact_persons = KontaktOsoba.objects.filter(company=appointment.company)
    
    context = {
        'appointment': appointment,
        'companies': companies,
        'contact_persons': contact_persons,
        'selected_contacts': [person.id for person in appointment.contact_persons.all()],
        'appointment_types': Appointment.APPOINTMENT_TYPE_CHOICES,
        'status_choices': Appointment.APPOINTMENT_STATUS_CHOICES,
    }
    return render(request, 'calendar/appointment_form.html', context)

def appointment_delete(request, pk):
    """View for deleting appointments"""
    if request.method == 'POST':
        appointment = Appointment.objects.get(pk=pk)
        appointment.delete()
        return JsonResponse({'status': 'success'})

def get_company_contacts(request):
    """API endpoint for getting company contacts"""
    company_id = request.GET.get('company_id')
    if not company_id:
        return JsonResponse({'contacts': []})
    
    contacts = KontaktOsoba.objects.filter(company_id=company_id).values('id', 'ime_prezime', 'pozicija')
    return JsonResponse({'contacts': list(contacts)})

def get_companies(request):
    """API endpoint for getting companies for autocomplete"""
    term = request.GET.get('term', '')
    companies = Company.objects.filter(name__icontains=term).values('id', 'name')[:10]
    results = [{'id': company['id'], 'value': company['name'], 'label': company['name']} for company in companies]
    return JsonResponse(results, safe=False)


# ---- CRUD operacije za standarde kompanije ----

def company_standard_create(request, company_id):
    """
    View za kreiranje novog standarda za kompaniju - AJAX endpoint
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Samo POST zahtevi su dozvoljeni.'}, status=405)
    
    company = get_object_or_404(Company, pk=company_id)
    
    try:
        standard_id = request.POST.get('standard_definition')
        issue_date = request.POST.get('issue_date') or None
        expiry_date = request.POST.get('expiry_date') or None
        notes = request.POST.get('notes', '')
        auditor_ids = request.POST.getlist('auditors[]')
        
        # Validacija
        if not standard_id:
            return JsonResponse({'success': False, 'error': 'Morate izabrati standard.'}, status=400)
        
        # Provera da li standard već postoji za kompaniju
        if CompanyStandard.objects.filter(company=company, standard_definition_id=standard_id).exists():
            return JsonResponse({'success': False, 'error': 'Kompanija već ima dodeljen ovaj standard.'}, status=400)
            
        # Napomena: Automatsko izračunavanje datuma isteka se vrši u metodi save() modela CompanyStandard
        
        # Konverzija string datuma u date objekte ako su stringovi
        if issue_date and isinstance(issue_date, str):
            from datetime import datetime
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        
        if expiry_date and isinstance(expiry_date, str):
            from datetime import datetime
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        
        # Kreiranje standarda
        company_standard = CompanyStandard.objects.create(
            company=company,
            standard_definition_id=standard_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            notes=notes
        )
        
        # Dodavanje auditora za standard
        # Konvertujemo auditor_ids u listu integera za lakše poređenje
        auditor_ids_int = [int(aid) for aid in auditor_ids if aid]
        added_auditors = 0
        
        # Dodajemo veze za izabrane auditore
        for auditor_id in auditor_ids_int:
            try:
                auditor = Auditor.objects.get(id=auditor_id)
                # Kreiramo novu vezu između auditora i standarda
                auditor_standard = AuditorStandard.objects.create(
                    auditor=auditor,
                    standard_id=standard_id,
                    datum_potpisivanja=datetime.now().date(),
                    napomena=f"Dodeljen za kompaniju {company.name}"
                )
                added_auditors += 1
            except Exception as e:
                print(f"Greška pri dodavanju auditora ID {auditor_id}: {str(e)}")
        
        # Pripremi odgovor
        message = f"Standard je uspešno dodat"
        if added_auditors > 0:
            message += f" sa {added_auditors} auditora"
        message += "."
        
        return JsonResponse({
            'success': True, 
            'message': message,
            'standard_id': company_standard.id,
            'standard_name': company_standard.standard_definition.standard
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Greška pri dodavanju standarda: {str(e)}'}, status=500)


def company_standard_update(request, company_id, pk):
    """
    View za ažuriranje postojećeg standarda kompanije
    """
    company = get_object_or_404(Company, pk=company_id)
    standard = get_object_or_404(CompanyStandard, pk=pk, company=company)
    
    if request.method == 'POST':
        standard_id = request.POST.get('standard_definition')
        issue_date = request.POST.get('issue_date') or None
        expiry_date = request.POST.get('expiry_date') or None
        notes = request.POST.get('notes', '')
        auditor_ids = request.POST.getlist('auditors[]')
        
        # Validacija
        if not standard_id:
            messages.error(request, "Morate izabrati standard.")
            return redirect('company:update', pk=company_id)
            
        # Napomena: Automatsko izračunavanje datuma isteka se vrši na backend strani
        
        # Konverzija string datuma u date objekte ako su stringovi
        if issue_date and isinstance(issue_date, str):
            from datetime import datetime
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        
        if expiry_date and isinstance(expiry_date, str):
            from datetime import datetime
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        
        # Ažuriranje standarda
        standard.standard_definition_id = standard_id
        standard.issue_date = issue_date
        standard.expiry_date = expiry_date
        standard.notes = notes
        standard.save()
        
        # Ažuriranje auditora za standard
        standard_def_id = standard.standard_definition_id
        
        # Dobavljamo sve postojeće veze između auditora i ovog standarda
        existing_auditor_standards = AuditorStandard.objects.filter(standard_id=standard_def_id)
        existing_auditor_ids = [as_obj.auditor.id for as_obj in existing_auditor_standards]
        
        # Konvertujemo auditor_ids u listu integera za lakše poređenje
        auditor_ids_int = [int(aid) for aid in auditor_ids]
        
        # Auditori koje treba dodati (oni koji su u novom spisku ali nisu u postojećim vezama)
        auditors_to_add = [aid for aid in auditor_ids_int if aid not in existing_auditor_ids]
        
        # Auditori koje treba ukloniti (oni koji su u postojećim vezama ali nisu u novom spisku)
        auditors_to_remove = [aid for aid in existing_auditor_ids if aid not in auditor_ids_int]
        
        # Dodajemo nove veze za izabrane auditore
        for auditor_id in auditors_to_add:
            try:
                auditor = Auditor.objects.get(id=auditor_id)
                # Kreiramo novu vezu između auditora i standarda
                auditor_standard = AuditorStandard.objects.create(
                    auditor=auditor,
                    standard_id=standard_def_id,
                    datum_potpisivanja=datetime.now().date(),
                    napomena=f"Dodeljen za kompaniju {company.name}"
                )
                messages.info(request, f"Auditor {auditor.ime_prezime} je uspešno dodeljen standardu.")
            except Exception as e:
                messages.warning(request, f"Greška pri dodavanju auditora ID {auditor_id}: {str(e)}")
                
        # Uklanjamo veze za auditore koji više nisu izabrani
        if auditors_to_remove:
            removed_count = AuditorStandard.objects.filter(
                standard_id=standard_def_id, 
                auditor_id__in=auditors_to_remove
            ).delete()[0]
            if removed_count > 0:
                messages.info(request, f"Uklonjeno {removed_count} auditora sa standarda.")
        
        
        messages.success(request, "Standard i auditori su uspešno ažurirani.")
        return redirect('company:update', pk=company_id)
    
    # GET zahtev
    # Dobavljamo sve auditore koji su kvalifikovani za ovaj standard
    all_auditors = Auditor.objects.all().order_by('ime_prezime')
    
    # Dobavljamo ID-jeve auditora koji su već dodeljeni ovom standardu
    selected_auditors = []
    standard_def_id = standard.standard_definition_id
    auditor_standards = AuditorStandard.objects.filter(standard_id=standard_def_id)
    selected_auditors = [as_obj.auditor.id for as_obj in auditor_standards]
    
    context = {
        'company': company,
        'standard': standard,
        'all_standard_definitions': StandardDefinition.objects.filter(active=True).order_by('code'),
        'all_auditors': all_auditors,
        'selected_auditors': selected_auditors,
    }
    return render(request, 'company/standard-update-form.html', context)


def company_standard_delete(request, company_id, pk):
    """
    View za brisanje standarda kompanije
    """
    company = get_object_or_404(Company, pk=company_id)
    standard = get_object_or_404(CompanyStandard, pk=pk, company=company)
    
    if request.method == 'POST':
        standard_name = standard.standard_definition.standard
        standard.delete()
        messages.success(request, f"Standard '{standard_name}' je uspešno obrisan.")
    else:
        messages.error(request, "Nije moguće obrisati standard. Potreban je POST zahtev.")
        
    return redirect('company:update', pk=company_id)


def company_standard_detail(request, company_id, pk):
    """
    View za pregled detalja standarda kompanije
    """
    company = get_object_or_404(Company, pk=company_id)
    standard = get_object_or_404(CompanyStandard, pk=pk, company=company)
    
    # Dobavljamo auditore za ovaj standard
    standard_def_id = standard.standard_definition_id
    auditor_standards = AuditorStandard.objects.filter(standard_id=standard_def_id)
    auditors = [as_obj.auditor for as_obj in auditor_standards]
    
    # Dobavljamo IAF/EAC kodove za ovaj standard (ako postoje)
    iaf_eac_codes = []
    try:
        from company.iaf_eac_models import CompanyStandardIafEac
        iaf_eac_codes = CompanyStandardIafEac.objects.filter(company_standard=standard)
    except ImportError:
        pass
    
    context = {
        'company': company,
        'standard': standard,
        'auditors': auditors,
        'iaf_eac_codes': iaf_eac_codes
    }
    
    return render(request, 'company/standard-detail.html', context)
