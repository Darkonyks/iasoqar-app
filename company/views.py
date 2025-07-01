import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Q, Count
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
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
                Q(mb__icontains=search_query)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
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
            standard_def_id = standard.standard_definition_id
            # Get auditors assigned to this standard
            auditor_standards = AuditorStandard.objects.filter(standard_id=standard_def_id)
            auditors = [as_obj.auditor for as_obj in auditor_standards]
            standards_with_auditors.append({
                'standard': standard,
                'auditors': auditors
            })
        
        context['standards'] = standards_with_auditors
        context['locations'] = company.ostale_lokacije.all()
        context['appointments'] = company.appointments.all().order_by('-start_datetime')[:5]
        
        # Get IAF/EAC codes for the company
        context['iaf_eac_codes'] = CompanyIAFEACCode.objects.filter(company=company).select_related('iaf_eac_code')
        
        # Get certification cycles for the company
        context['certification_cycles'] = company.certification_cycles.all().order_by('-start_date')
        
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
    template_name = 'company/audit-list.html'
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
                    'pending': 'in_progress',
                    'completed': 'completed',
                    'cancelled': 'cancelled'
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
    template_name = 'company/company-audits.html'
    
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
    template_name = 'company/audit-detail.html'
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
    template_name = 'company/audit-confirm-delete.html'
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


class CalendarView(TemplateView):
    template_name = 'calendar/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add companies for the appointment form
        context['companies'] = Company.objects.all().order_by('name')
        return context

class CalendarEventsView(TemplateView):
    template_name = 'calendar/calendar_events.html'

def dashboard(request):
    # Calculate total companies
    total_companies = Company.objects.count()
    
    # Calculate active companies and certificates
    active_companies = Company.objects.filter(
        certificate_status=Company.STATUS_ACTIVE
    ).count()
    
    # Count active certificates (standards associated with active companies)
    active_certificates = CompanyStandard.objects.filter(
        company__certificate_status=Company.STATUS_ACTIVE
    ).count()
    
    # Calculate expired certificates
    expired_certificates = Company.objects.filter(
        certificate_status=Company.STATUS_EXPIRED
    ).count()
    
    # Get audits scheduled for the current work week
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday
    next_month = today + timedelta(days=30)  # Definisanje sledećeg meseca za upite
    
    # Get planned audits for this week
    this_week_audits = []
    
    # Auditi koji ističu uskoro - sad koristimo novi model CycleAudit
    from .cycle_models import CycleAudit
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
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
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

def appointment_calendar_json(request):
    """API endpoint for getting appointment data in FullCalendar format"""
    # Get all appointments
    appointments = Appointment.objects.all()
    events = []
    
    # Add appointments to events
    for appointment in appointments:
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
                'eventType': 'appointment'
            }
        })
    
    # Stari model NaredneProvere je uklonjen - sada se koristi samo novi model CycleAudit
    
    # Get all audit dates from the new model (CycleAudit)
    from .cycle_models import CycleAudit
    cycle_audits = CycleAudit.objects.all().select_related('certification_cycle__company')
    
    audit_type_mapping = {
        'surveillance_1': {
            'name': 'Prva nadzorna provera',
            'color_planned': '#FF9800',
            'color_completed': '#4CAF50'
        },
        'surveillance_2': {
            'name': 'Druga nadzorna provera',
            'color_planned': '#FF9800',
            'color_completed': '#4CAF50'
        },
        'recertification': {
            'name': 'Resertifikacija',
            'color_planned': '#E91E63',
            'color_completed': '#4CAF50'
        }
    }
    
    # Add cycle audit dates to events
    for audit in cycle_audits:
        # Get company name from certification cycle
        company_name = audit.certification_cycle.company.name
        audit_type_info = audit_type_mapping.get(audit.audit_type, {})
        audit_name = audit_type_info.get('name', 'Audit')
        
        # Determine audit status and color
        is_completed = audit.audit_status in ['completed']
        status_text = '(održana)' if is_completed else '(planirana)'
        color = audit_type_info.get('color_completed' if is_completed else 'color_planned', '#3788d8')
        
        # Add planned audit
        if audit.planned_date:
            events.append({
                'id': f'cycle_audit_planned_{audit.id}',
                'title': f'{audit_name} {status_text} - {company_name}',
                'start': audit.planned_date.isoformat(),
                'allDay': True,
                'color': color,
                'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': audit_name,
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'cycle_audit',
                    'auditStatus': 'planned' if not is_completed else 'completed',
                    'modelType': 'new',
                    'notes': audit.notes or 'N/A'
                }
            })
        
        # Add completed audit
        if audit.actual_date:
            events.append({
                'id': f'cycle_audit_actual_{audit.id}',
                'title': f'{audit_name} (održana) - {company_name}',
                'start': audit.actual_date.isoformat(),
                'allDay': True,
                'color': '#4CAF50',  # Green for completed audit events
                'url': f'/company/audits/{audit.id}/update/',
                'extendedProps': {
                    'company': company_name,
                    'type': audit_name,
                    'audit_type': audit.audit_type,
                    'status': dict(audit.AUDIT_STATUS_CHOICES)[audit.audit_status],
                    'cycle_id': audit.certification_cycle.id,
                    'eventType': 'cycle_audit',
                    'auditStatus': 'completed',
                    'modelType': 'new',
                    'notes': audit.notes or 'N/A'
                }
            })
    
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
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
    View za kreiranje novog standarda za kompaniju
    """
    company = get_object_or_404(Company, pk=company_id)
    
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
        
        # Provera da li standard već postoji za kompaniju
        if CompanyStandard.objects.filter(company=company, standard_definition_id=standard_id).exists():
            messages.error(request, "Kompanija već ima dodeljen ovaj standard.")
            return redirect('company:update', pk=company_id)
            
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
            except Exception as e:
                messages.warning(request, f"Greška pri dodavanju auditora ID {auditor_id}: {str(e)}")
        
        if auditor_ids:
            messages.success(request, f"Standard je uspešno dodat sa {len(auditor_ids)} auditora.")
        else:
            messages.success(request, "Standard je uspešno dodat.")
        return redirect('company:update', pk=company_id)
    
    # GET zahtev (opciono, ako želite zasebnu stranicu za dodavanje standarda)
    return redirect('company:update', pk=company_id)


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
