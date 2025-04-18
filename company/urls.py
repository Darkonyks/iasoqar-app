from django.urls import path
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
    get_companies
)

app_name = 'company'

urlpatterns = [
    # Calendar and appointment URLs
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar/events/', CalendarEventsView.as_view(), name='calendar_events'),
    path('calendar/api/events/', appointment_calendar_json, name='appointment_calendar_json'),
    path('appointments/create/', appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/', appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/update/', appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/delete/', appointment_delete, name='appointment_delete'),
    
    # API endpoints
    path('api/company-contacts/', get_company_contacts, name='get_company_contacts'),
    path('api/companies/', get_companies, name='get_companies'),
    
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
    path('audits/create/', AuditCreateView.as_view(), name='audit_create'),
    path('audits/<int:pk>/', CompanyAuditDetailView.as_view(), name='audit_detail'),
    path('audits/<int:pk>/update/', AuditUpdateView.as_view(), name='audit_update'),
    path('audits/<int:pk>/delete/', AuditDeleteView.as_view(), name='audit_delete'),
]
