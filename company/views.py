from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
import json
from .models import Company, NaredneProvere, Appointment, KontaktOsoba, OstalaLokacija, IAFEACCode, CompanyIAFEACCode
from .standard_models import StandardDefinition, CompanyStandard
from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from datetime import datetime, timedelta
from django.db.models import Count
import random
from .forms import AuditForm, CompanyForm

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


class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company/company-detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        # Get related data
        context['contact_persons'] = company.kontakt_osobe.all().order_by('-is_primary', 'ime_prezime')
        context['standards'] = company.company_standards.all()  # Ispravka: standards -> company_standards
        context['locations'] = company.ostale_lokacije.all()
        context['appointments'] = company.appointments.all().order_by('-start_datetime')[:5]
        
        # Get IAF/EAC codes for the company
        context['iaf_eac_codes'] = CompanyIAFEACCode.objects.filter(company=company).select_related('iaf_eac_code')
        
        # Get audit information if available
        try:
            context['audit_info'] = company.naredne_provere.first()
        except:
            context['audit_info'] = None
            
        return context


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
        # Dodaj sve definicije standarda za izbor
        from .standard_models import StandardDefinition
        context['all_standard_definitions'] = StandardDefinition.objects.filter(active=True).order_by('code')
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


class AuditListView(ListView):
    model = NaredneProvere
    template_name = 'company/audit-list.html'
    context_object_name = 'audits'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('company')
        
        # Filter by company if specified
        company_id = self.request.GET.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by status if specified
        status = self.request.GET.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by date range if specified
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            # Filter audits with any date after date_from
            queryset = queryset.filter(
                Q(first_surv_due__gte=date_from) | 
                Q(second_surv_due__gte=date_from) | 
                Q(trinial_audit_due__gte=date_from)
            )
            
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Filter audits with any date before date_to
            queryset = queryset.filter(
                Q(first_surv_due__lte=date_to) | 
                Q(second_surv_due__lte=date_to) | 
                Q(trinial_audit_due__lte=date_to)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add companies for filtering
        context['companies'] = Company.objects.all().order_by('name')
        
        # Add status choices for filtering
        context['status_choices'] = NaredneProvere.AUDIT_STATUS_CHOICES
        
        # Add filter values
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Add today's date for template comparison
        context['today'] = datetime.now()
        
        return context


class CompanyAuditDetailView(DetailView):
    model = NaredneProvere
    template_name = 'company/audit-detail.html'
    context_object_name = 'audit'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audit = self.get_object()
        
        # Get related calendar events
        context['calendar_events'] = audit.calendar_events.all().order_by('start')
        
        # Get company details
        context['company'] = audit.company
        
        # Get company standards
        context['standards'] = audit.company.standards.all()
        
        # Add today's date for template comparison
        context['today'] = datetime.now()
        
        return context


class AuditCreateView(CreateView):
    model = NaredneProvere
    form_class = AuditForm
    template_name = 'company/audit-form.html'
    success_url = reverse_lazy('company:audit_list')
    
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


class AuditUpdateView(UpdateView):
    model = NaredneProvere
    form_class = AuditForm
    template_name = 'company/audit-form.html'
    
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


class AuditDeleteView(DeleteView):
    model = NaredneProvere
    template_name = 'company/audit-confirm-delete.html'
    success_url = reverse_lazy('company:audit_list')
    context_object_name = 'audit'
    
    def delete(self, request, *args, **kwargs):
        audit = self.get_object()
        messages.success(request, f"Nadzorna provera za kompaniju {audit.company.name} je uspešno obrisana.")
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
    
    # Get planned audits for this week
    this_week_audits = []
    
    # Check first surveillance audits
    first_audits = NaredneProvere.objects.filter(
        first_surv_due__range=(start_of_week, end_of_week)
    ).select_related('company')
    
    for audit in first_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.company.name,
            'type': 'Prva nadzorna provera',
            'date': audit.first_surv_due,
            'status': audit.get_status_display()
        })
    
    # Check second surveillance audits
    second_audits = NaredneProvere.objects.filter(
        second_surv_due__range=(start_of_week, end_of_week)
    ).select_related('company')
    
    for audit in second_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.company.name,
            'type': 'Druga nadzorna provera',
            'date': audit.second_surv_due,
            'status': audit.get_status_display()
        })
    
    # Check recertification audits
    recert_audits = NaredneProvere.objects.filter(
        trinial_audit_due__range=(start_of_week, end_of_week)
    ).select_related('company')
    
    for audit in recert_audits:
        this_week_audits.append({
            'id': audit.id,
            'company': audit.company.name,
            'type': 'Resertifikacija',
            'date': audit.trinial_audit_due,
            'status': audit.get_status_display()
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

    # Calculate audit status distribution
    audit_status = NaredneProvere.objects.values('status').annotate(
        total=Count('status')
    )
    
    # Prepare audit chart data
    audit_labels = [str(dict(NaredneProvere.AUDIT_STATUS_CHOICES).get(status['status']))
                   for status in audit_status]
    audit_data = [status['total'] for status in audit_status]
    
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
    
    # Get all audit dates
    audits = NaredneProvere.objects.all()
    
    # Add audit dates to events
    for audit in audits:
        # Add planned first surveillance audit
        if audit.first_surv_due:
            events.append({
                'id': f'audit_first_due_{audit.id}',
                'title': f'Prva nadzorna provera (planirana) - {audit.company.name}',
                'start': audit.first_surv_due.isoformat(),
                'allDay': True,
                'color': '#FF9800',  # Orange for planned audit events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Prva nadzorna provera',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'planned'
                }
            })
        
        # Add completed first surveillance audit
        if audit.first_surv_cond:
            events.append({
                'id': f'audit_first_cond_{audit.id}',
                'title': f'Prva nadzorna provera (održana) - {audit.company.name}',
                'start': audit.first_surv_cond.isoformat(),
                'allDay': True,
                'color': '#4CAF50',  # Green for completed audit events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Prva nadzorna provera',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'completed'
                }
            })
        
        # Add planned second surveillance audit
        if audit.second_surv_due:
            events.append({
                'id': f'audit_second_due_{audit.id}',
                'title': f'Druga nadzorna provera (planirana) - {audit.company.name}',
                'start': audit.second_surv_due.isoformat(),
                'allDay': True,
                'color': '#FF9800',  # Orange for planned audit events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Druga nadzorna provera',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'planned'
                }
            })
        
        # Add completed second surveillance audit
        if audit.second_surv_cond:
            events.append({
                'id': f'audit_second_cond_{audit.id}',
                'title': f'Druga nadzorna provera (održana) - {audit.company.name}',
                'start': audit.second_surv_cond.isoformat(),
                'allDay': True,
                'color': '#4CAF50',  # Green for completed audit events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Druga nadzorna provera',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'completed'
                }
            })
        
        # Add planned recertification audit
        if audit.trinial_audit_due:
            events.append({
                'id': f'audit_recert_due_{audit.id}',
                'title': f'Resertifikacija (planirana) - {audit.company.name}',
                'start': audit.trinial_audit_due.isoformat(),
                'allDay': True,
                'color': '#E91E63',  # Pink for planned recertification events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Resertifikacija',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'planned'
                }
            })
        
        # Add completed recertification audit
        if audit.trinial_audit_cond:
            events.append({
                'id': f'audit_recert_cond_{audit.id}',
                'title': f'Resertifikacija (održana) - {audit.company.name}',
                'start': audit.trinial_audit_cond.isoformat(),
                'allDay': True,
                'color': '#2196F3',  # Blue for completed recertification events
                'url': f'/company/audits/{audit.id}/',
                'extendedProps': {
                    'company': audit.company.name,
                    'type': 'Resertifikacija',
                    'status': audit.get_status_display(),
                    'eventType': 'audit',
                    'auditStatus': 'completed'
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
        
        # Validacija
        if not standard_id:
            messages.error(request, "Morate izabrati standard.")
            return redirect('company:update', pk=company_id)
        
        # Provera da li standard već postoji za kompaniju
        if CompanyStandard.objects.filter(company=company, standard_definition_id=standard_id).exists():
            messages.error(request, "Kompanija već ima dodeljen ovaj standard.")
            return redirect('company:update', pk=company_id)
            
        # Kreiranje standarda
        CompanyStandard.objects.create(
            company=company,
            standard_definition_id=standard_id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            notes=notes
        )
        
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
        
        messages.success(request, "Standard je uspešno ažuriran.")
        return redirect('company:update', pk=company_id)
    
    # GET zahtev
    context = {
        'company': company,
        'standard': standard,
        'all_standard_definitions': StandardDefinition.objects.filter(active=True).order_by('code'),
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
