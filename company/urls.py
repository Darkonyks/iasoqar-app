from django.urls import path
from .auditor_views import AuditorListView, AuditorDetailView, AuditorDeleteView, AuditorCreateView, AuditorUpdateView, auditor_standard_create, auditor_standard_update, auditor_standard_delete, auditor_standard_iaf_eac_create, auditor_standard_iaf_eac_update, auditor_standard_iaf_eac_delete, get_auditor_details, get_qualified_auditors
from .contact_views import kontakt_osoba_create, kontakt_osoba_update, kontakt_osoba_delete
from .location_views import LocationListView, LocationDetailView, LocationCreateView, LocationUpdateView, LocationDeleteView
from .views_cycles import (CertificationCycleListView, CertificationCycleDetailView, CertificationCycleCreateView, 
                         CertificationCycleUpdateView, CertificationCycleDeleteView, CycleAuditCreateView, 
                         CycleAuditUpdateView, CycleAuditDeleteView)
from .views import (
    CalendarView, 
    CalendarEventsView, 
    dashboard, 
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
    AuditListView,
    CompanyAuditsView,
    CompanyAuditDetailView,
    AuditCreateView,
    AuditUpdateView,
    AuditDeleteView,
    appointment_calendar_json, 
    appointment_detail, 
    appointment_create, 
    appointment_update, 
    appointment_delete,
    get_company_contacts,
    get_companies,
    audit_detail_json,
    # Standard CRUD funkcije
    company_standard_create,
    company_standard_update,
    company_standard_delete
)

# Import za AJAX funkcije
from .views_ajax import (
    delete_standard,
    add_iaf_eac_code,
    delete_iaf_eac_code,
    update_iaf_eac_primary,
    list_iaf_eac_codes,
    certification_cycle_json,
    audit_days_by_audit_id,
    update_event_date
)

app_name = 'company'

urlpatterns = [
    # Calendar and appointment URLs
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar/events/', CalendarEventsView.as_view(), name='calendar_events'),
    path('calendar/api/events/', appointment_calendar_json, name='appointment_calendar_json'),
    path('audits/<int:pk>/detail/', audit_detail_json, name='audit_detail_json'),
    path('appointments/create/', appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/', appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/update/', appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/delete/', appointment_delete, name='appointment_delete'),
    
    # API endpoints
    path('api/company-contacts/', get_company_contacts, name='get_company_contacts'),
    path('api/companies/', get_companies, name='get_companies'),
    
    # Standardi CRUD URLs
    path('companies/<int:company_id>/standards/add/', company_standard_create, name='standard_create'),
    path('companies/<int:company_id>/standards/<int:pk>/update/', company_standard_update, name='standard_update'),
    path('companies/<int:company_id>/standards/<int:pk>/delete/', company_standard_delete, name='standard_delete'),
    
    # AJAX URL-ovi za standarde
    path('api/standards/delete/', delete_standard, name='api_standard_delete'),
    
    # IAF/EAC Kodovi CRUD URLs
    path('companies/<int:company_id>/iaf-eac/add/', add_iaf_eac_code, name='iaf_eac_add'),
    path('company/companies/<int:company_id>/iaf-eac/add/', add_iaf_eac_code, name='iaf_eac_add_with_prefix'),
    
    # Dodatne putanje za IAF/EAC kodove koje koristi JavaScript
    path('companies/<int:company_id>/iaf-eac/<int:code_id>/delete/', delete_iaf_eac_code, name='iaf_eac_delete'),
    path('company/companies/<int:company_id>/iaf-eac/<int:code_id>/delete/', delete_iaf_eac_code, name='iaf_eac_delete_with_prefix'),
    path('companies/<int:company_id>/iaf-eac/<int:code_id>/set-primary/', update_iaf_eac_primary, name='iaf_eac_set_primary'),
    path('company/companies/<int:company_id>/iaf-eac/<int:code_id>/set-primary/', update_iaf_eac_primary, name='iaf_eac_set_primary_with_prefix'),
    
    # Putanja za listanje IAF/EAC kodova
    path('companies/<int:company_id>/iaf-eac/list/', list_iaf_eac_codes, name='iaf_eac_list'),
    path('company/companies/<int:company_id>/iaf-eac/list/', list_iaf_eac_codes, name='iaf_eac_list_with_prefix'),
    
    # Postojeće API putanje (zadržavamo ih zbog kompatibilnosti)
    path('api/iaf-eac/delete/', delete_iaf_eac_code, name='api_iaf_eac_delete'),
    path('api/iaf-eac/update-primary/', update_iaf_eac_primary, name='api_iaf_eac_update_primary'),
    
    # API endpoint za certifikacione cikluse
    path('api/cycles/<int:pk>/json/', certification_cycle_json, name='certification_cycle_json'),
    
    # API endpoint za audit dane prema ID-u audita
    path('api/audit-days/by-audit/<int:audit_id>/', audit_days_by_audit_id, name='audit_days_by_audit_id'),
    
    # API endpoint za ažuriranje datuma događaja nakon drag-and-drop
    path('api/events/update-date/', update_event_date, name='update_event_date'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Company CRUD URLs
    path('companies/', CompanyListView.as_view(), name='list'),
    path('companies/create/', CompanyCreateView.as_view(), name='create'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='detail'),
    path('companies/<int:pk>/update/', CompanyUpdateView.as_view(), name='update'),
    path('companies/<int:pk>/delete/', CompanyDeleteView.as_view(), name='delete'),
    
    # Audit CRUD URLs
    path('audits/', AuditListView.as_view(), name='audit_list'),
    path('companies/<int:company_id>/audits/', CompanyAuditsView.as_view(), name='company_audits'),
    path('audits/create/', AuditCreateView.as_view(), name='audit_create'),
    path('audits/<int:pk>/', CompanyAuditDetailView.as_view(), name='audit_detail'),
    path('old-audits/<int:pk>/update/', AuditUpdateView.as_view(), name='audit_update'),  # Promenjen URL za stare audite
    path('audits/<int:pk>/delete/', AuditDeleteView.as_view(), name='audit_delete'),
    
    # Auditor CRUD URLs
    path('auditors/', AuditorListView.as_view(), name='auditor_list'),
    path('auditors/create/', AuditorCreateView.as_view(), name='auditor_create'),
    path('auditors/<int:pk>/', AuditorDetailView.as_view(), name='auditor_detail'),
    path('auditors/<int:pk>/update/', AuditorUpdateView.as_view(), name='auditor_update'),
    path('auditors/<int:pk>/delete/', AuditorDeleteView.as_view(), name='auditor_delete'),
    path('auditors/<int:auditor_id>/standards/add/', auditor_standard_create, name='auditor_standard_create'),
    path('auditors/<int:auditor_id>/standards/<int:pk>/update/', auditor_standard_update, name='auditor_standard_update'),
    path('auditors/<int:auditor_id>/standards/<int:pk>/delete/', auditor_standard_delete, name='auditor_standard_delete'),
    path('auditor-standards/<int:standard_id>/iaf-eac/add/', auditor_standard_iaf_eac_create, name='auditor_standard_iaf_eac_create'),
    path('auditor-standards/<int:standard_id>/iaf-eac/<int:pk>/update/', auditor_standard_iaf_eac_update, name='auditor_standard_iaf_eac_update'),
    path('auditor-standards/<int:standard_id>/iaf-eac/<int:pk>/delete/', auditor_standard_iaf_eac_delete, name='auditor_standard_iaf_eac_delete'),
    path('api/auditors/<int:pk>/details/', get_auditor_details, name='auditor_details_api'),
    path('api/qualified-auditors/', get_qualified_auditors, name='qualified_auditors_api'),
    
    # Kontakt osobe CRUD URLs
    path('companies/<int:company_id>/kontakt/create/', kontakt_osoba_create, name='kontakt_create'),
    path('companies/<int:company_id>/kontakt/<int:pk>/update/', kontakt_osoba_update, name='kontakt_update'),
    path('companies/<int:company_id>/kontakt/<int:pk>/delete/', kontakt_osoba_delete, name='kontakt_delete'),
    
    # Lokacije CRUD URLs
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/create/', LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('locations/<int:pk>/update/', LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),
    
    # Certification Cycles CRUD URLs
    path('cycles/', CertificationCycleListView.as_view(), name='cycle_list'),
    path('cycles/create/', CertificationCycleCreateView.as_view(), name='cycle_create'),
    path('companies/<int:company_id>/cycles/create/', CertificationCycleCreateView.as_view(), name='company_cycle_create'),
    path('cycles/<int:pk>/', CertificationCycleDetailView.as_view(), name='cycle_detail'),
    path('cycles/<int:pk>/update/', CertificationCycleUpdateView.as_view(), name='cycle_update'),
    path('cycles/<int:pk>/delete/', CertificationCycleDeleteView.as_view(), name='cycle_delete'),
    
    # Cycle Audit CRUD URLs
    path('cycles/<int:cycle_id>/audits/create/', CycleAuditCreateView.as_view(), name='cycle_audit_create'),
    path('audits/<int:pk>/update/', CycleAuditUpdateView.as_view(), name='cycle_audit_update'),
    path('audits/<int:pk>/delete/', CycleAuditDeleteView.as_view(), name='cycle_audit_delete'),
]
