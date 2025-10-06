from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .srbija_tim_models import SrbijaTim
from .forms import SrbijaTimForm
import logging
import json
from datetime import datetime

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


class SrbijaTimAuditorScheduleView(LoginRequiredMixin, ListView):
    """
    Lista stvarnih sastanaka sa auditorima - raspored auditora
    """
    model = SrbijaTim
    template_name = 'srbija_tim/auditor_schedule.html'
    context_object_name = 'visits'
    
    def get_queryset(self):
        return SrbijaTim.objects.all().prefetch_related(
            'standards',
            'auditors',
            'company'
        ).select_related('created_by').order_by('-visit_date', 'visit_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Srbija Tim - Raspored Auditora'
        
        # Grupisanje po auditorima
        from collections import defaultdict
        auditor_visits = defaultdict(list)
        
        for visit in self.get_queryset():
            for auditor in visit.auditors.all():
                auditor_visits[auditor].append(visit)
        
        context['auditor_visits'] = dict(auditor_visits)
        
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
        
        # Ako postoji vreme, kombinuj datum i vreme (proveri da li polje postoji)
        visit_time = getattr(visit, 'visit_time', None)
        if visit_time:
            start_datetime = datetime.combine(visit.visit_date, visit_time)
            event_start = start_datetime.isoformat()
            all_day = False
        else:
            event_start = visit.visit_date.isoformat()
            all_day = True
        
        events.append({
            'id': visit.id,
            'title': f'{visit.certificate_number} - {visit.company.name}',
            'start': event_start,
            'allDay': all_day,
            'color': color,
            'extendedProps': {
                'certificate_number': visit.certificate_number,
                'company_name': visit.company.name,
                'standards': visit.get_standards_display(),
                'auditors': visit.get_auditors_display(),
                'report_sent': visit.report_sent,
                'certificate_expiry_date': visit.certificate_expiry_date.isoformat() if visit.certificate_expiry_date else None,
                'notes': visit.notes or '',
                'visit_time': visit_time.isoformat() if visit_time else None,
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
@require_http_methods(["POST"])
def srbija_tim_update_date(request, pk):
    """
    Ažuriranje datuma i vremena posete preko drag & drop u kalendaru
    """
    try:
        visit = get_object_or_404(SrbijaTim, pk=pk)
        
        # Parsiranje JSON podataka iz zahteva
        data = json.loads(request.body)
        new_date_str = data.get('visit_date')
        new_time_str = data.get('visit_time')  # Opciono vreme
        
        if not new_date_str:
            return JsonResponse({
                'success': False,
                'message': 'Datum nije prosleđen.'
            }, status=400)
        
        # Parsiranje datuma
        try:
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Neispravan format datuma.'
            }, status=400)
        
        # Parsiranje vremena (opciono)
        new_time = None
        if new_time_str:
            try:
                new_time = datetime.strptime(new_time_str, '%H:%M:%S').time()
            except ValueError:
                try:
                    # Pokušaj sa formatom bez sekundi
                    new_time = datetime.strptime(new_time_str, '%H:%M').time()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Neispravan format vremena.'
                    }, status=400)
        
        # Ažuriranje datuma i vremena
        old_date = visit.visit_date
        old_time = getattr(visit, 'visit_time', None)
        visit.visit_date = new_date
        
        # Postavi visit_time samo ako polje postoji u modelu
        if hasattr(visit, 'visit_time'):
            visit.visit_time = new_time
        
        visit.save()
        
        log_message = f'Srbija Tim poseta {visit.certificate_number} - datum promenjen sa {old_date} na {new_date}'
        if new_time:
            log_message += f', vreme: {old_time or "N/A"} -> {new_time}'
        log_message += f' od strane korisnika {request.user.username}'
        
        logger.info(log_message)
        
        response_data = {
            'success': True,
            'message': 'Datum posete je uspešno ažuriran.',
            'new_date': new_date.isoformat()
        }
        if new_time:
            response_data['new_time'] = new_time.isoformat()
            response_data['message'] = 'Datum i vreme posete su uspešno ažurirani.'
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Neispravan JSON format.'
        }, status=400)
    except Exception as e:
        logger.error(f'Greška pri ažuriranju datuma Srbija Tim posete: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Greška pri ažuriranju datuma: {str(e)}'
        }, status=500)
