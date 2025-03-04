from django.urls import path
from .views import CalendarView, CalendarEventsView, dashboard, CompanyListView

app_name = 'company'

urlpatterns = [
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('calendar/events/', CalendarEventsView.as_view(), name='calendar_events'),
    path('dashboard/', dashboard, name='dashboard'),
    path('list/', CompanyListView.as_view(), name='list'),
]
