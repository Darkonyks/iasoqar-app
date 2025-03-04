from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.db.models import Count, Q
import json
from .models import Company, NaredneProvere
from datetime import datetime
from django.db.models import Count
import random

class CompanyListView(ListView):
    model = Company
    template_name = 'company/company-list.html'
    context_object_name = 'companies'

class CalendarView(TemplateView):
    template_name = 'calendar/calendar.html'

class CalendarEventsView(TemplateView):
    template_name = 'calendar/calendar_events.html'

def dashboard(request):
    # Calculate total companies
    total_companies = Company.objects.count()
    
    # Calculate active companies and certificates
    active_companies = Company.objects.filter(
        certificate_status=Company.STATUS_ACTIVE
    ).count()
    
    active_certificates = Company.objects.filter(
        certificate_status=Company.STATUS_ACTIVE
    ).aggregate(total_certificates=Count('id'))['total_certificates']
    
    # Calculate expired certificates
    expired_certificates = Company.objects.filter(
        certificate_status=Company.STATUS_EXPIRED
    ).count()
    
    # Get standards distribution
    standards_distribution = Company.objects.values('standards__standard').annotate(
        total=Count('standards')
    ).order_by('-total')
    
    # Prepare chart data
    standards_labels = [item['standards__standard'] for item in standards_distribution]
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
    standards_distribution = Company.objects.values('standards__standard').annotate(
        total=Count('standards')
    ).order_by('-total')
    
    # Handle null standards and format for Chart.js
    standards_labels = [item['standards__standard'] or 'No Standard' for item in standards_distribution]
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
    }
    
    return render(request, 'dashboard.html', context)
