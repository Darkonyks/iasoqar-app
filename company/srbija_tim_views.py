from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .srbija_tim_models import SrbijaTim
from .forms import SrbijaTimForm
import logging

logger = logging.getLogger(__name__)


class SrbijaTimCalendarView(LoginRequiredMixin, ListView):
    """
    Glavna stranica sa kalendarom za Srbija Tim posete
    """
    model = SrbijaTim
    template_name = 'srbija_tim/calendar.html'
    context_object_name = 'visits'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Srbija Tim - Crni Kalendar'
        return context


class SrbijaTimListView(LoginRequiredMixin, ListView):
    """
    Lista svih poseta u tabelarnom prikazu
    """
    model = SrbijaTim
    template_name = 'srbija_tim/list.html'
    context_object_name = 'visits'
    paginate_by = None  # Koristimo DataTables za paginaciju
    
    def get_queryset(self):
        return SrbijaTim.objects.all().prefetch_related(
            'standards',
            'auditors',
            'company'
        ).select_related('created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Srbija Tim - Lista Poseta'
        return context


class SrbijaTimCreateView(LoginRequiredMixin, CreateView):
    """
    Kreiranje nove posete
    """
    model = SrbijaTim
    form_class = SrbijaTimForm
    template_name = 'srbija_tim/form.html'
    success_url = reverse_lazy('company:srbija_tim_calendar')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Poseta - Srbija Tim'
        context['action'] = 'create'
        return context


class SrbijaTimUpdateView(LoginRequiredMixin, UpdateView):
    """
    Izmena postojeće posete
    """
    model = SrbijaTim
    form_class = SrbijaTimForm
    template_name = 'srbija_tim/form.html'
    success_url = reverse_lazy('company:srbija_tim_calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Izmeni Posetu - {self.object.certificate_number}'
        context['action'] = 'update'
        return context


class SrbijaTimDeleteView(LoginRequiredMixin, DeleteView):
    """
    Brisanje posete
    """
    model = SrbijaTim
    template_name = 'srbija_tim/confirm_delete.html'
    success_url = reverse_lazy('company:srbija_tim_calendar')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Obriši Posetu - {self.object.certificate_number}'
        return context


class SrbijaTimDetailView(LoginRequiredMixin, DetailView):
    """
    Detalji posete
    """
    model = SrbijaTim
    template_name = 'srbija_tim/detail.html'
    context_object_name = 'visit'
    
    def get_queryset(self):
        return SrbijaTim.objects.all().prefetch_related(
            'standards',
            'auditors',
            'company'
        ).select_related('created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Detalji Posete - {self.object.certificate_number}'
        return context


def srbija_tim_calendar_json(request):
    """
    JSON endpoint za FullCalendar - vraća sve posete kao događaje
    """
    visits = SrbijaTim.objects.all().prefetch_related('standards', 'auditors')
    
    events = []
    for visit in visits:
        # Boja na osnovu statusa
        if visit.report_sent:
            color = '#28a745'  # Zelena - poslat izveštaj
        else:
            color = '#dc3545'  # Crvena - nije poslat izveštaj
        
        # Provera da li je sertifikat istekao
        if visit.is_certificate_expired():
            color = '#6c757d'  # Siva - istekao sertifikat
        
        events.append({
            'id': visit.id,
            'title': f'{visit.certificate_number} - {visit.company_name}',
            'start': visit.visit_date.isoformat(),
            'allDay': True,
            'color': color,
            'extendedProps': {
                'certificate_number': visit.certificate_number,
                'company_name': visit.company_name,
                'standards': visit.get_standards_display(),
                'auditors': visit.get_auditors_display(),
                'report_sent': visit.report_sent,
                'certificate_expiry_date': visit.certificate_expiry_date.isoformat() if visit.certificate_expiry_date else None,
                'notes': visit.notes or '',
            }
        })
    
    return JsonResponse(events, safe=False)
