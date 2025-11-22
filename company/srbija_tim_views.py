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
        queryset = SrbijaTim.objects.all().prefetch_related(
            'standards',
            'auditors',
            'company'
        ).select_related('created_by')
        
        # Filtriranje po datumu
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(visit_date__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(visit_date__lte=date_to_obj)
            except ValueError:
                pass
        
        return queryset.order_by('-visit_date', 'visit_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Srbija Tim - Raspored Auditora'
        
        # Prosleđivanje filter parametara u template
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
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
    
    def get_initial(self):
        """
        Postavi inicijalne vrednosti forme - datum iz URL parametra
        """
        initial = super().get_initial()
        
        # Ako je datum prosleđen kao URL parametar, postavi ga kao inicijalnu vrednost
        date_param = self.request.GET.get('date')
        if date_param:
            try:
                from datetime import datetime
                # Parsiranje datuma iz URL-a (format: YYYY-MM-DD)
                selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                initial['visit_date'] = selected_date
            except ValueError:
                pass  # Ako format nije ispravan, ignoriši
        
        return initial
    
    def form_valid(self, form):
        from datetime import timedelta
        from django.contrib import messages
        import uuid
        
        # Dobij broj dana posete
        broj_dana = form.cleaned_data.get('broj_dana_posete')
        
        # Ako nije unet broj dana ili je manji od 1, kreiraj samo jedan zapis
        if not broj_dana or broj_dana < 1:
            form.instance.created_by = self.request.user
            return super().form_valid(form)
        
        # Zaokruži broj dana na ceo broj
        broj_dana_int = int(broj_dana)
        
        # Generiši jedinstveni group_id za ovu grupu poseta
        group_id = str(uuid.uuid4())
        
        # Sačuvaj podatke iz forme
        visit_date = form.cleaned_data.get('visit_date')
        certificate_number = form.cleaned_data.get('certificate_number')
        company = form.cleaned_data.get('company')
        standards = form.cleaned_data.get('standards')
        certificate_expiry_date = form.cleaned_data.get('certificate_expiry_date')
        auditors = form.cleaned_data.get('auditors')
        visit_time = form.cleaned_data.get('visit_time')
        status = form.cleaned_data.get('status')
        report_sent = form.cleaned_data.get('report_sent')
        notes = form.cleaned_data.get('notes')
        
        # Kreiraj zapise za svaki dan
        created_visits = []
        for i in range(broj_dana_int):
            # Izračunaj datum za ovaj dan (prvi dan je visit_date, drugi je visit_date + 1 dan, itd.)
            current_date = visit_date + timedelta(days=i) if visit_date else None
            
            # Kreiraj novi zapis
            visit = SrbijaTim(
                certificate_number=certificate_number,
                company=company,
                certificate_expiry_date=certificate_expiry_date,
                visit_date=current_date,
                visit_time=visit_time,
                broj_dana_posete=broj_dana,
                group_id=group_id,
                status=status,
                report_sent=report_sent,
                notes=notes,
                created_by=self.request.user
            )
            visit.save()
            
            # Dodaj many-to-many relacije
            if standards:
                visit.standards.set(standards)
            if auditors:
                visit.auditors.set(auditors)
            
            created_visits.append(visit)
        
        # Dodaj poruku o uspešnom kreiranju
        messages.success(
            self.request, 
            f'Uspešno kreirano {broj_dana_int} poseta za period od {broj_dana_int} dana.'
        )
        
        # Preusmeri na success_url
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.success_url)
    
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
    
    def form_valid(self, form):
        from datetime import timedelta
        from django.contrib import messages
        import uuid
        
        # Dobij trenutni objekat
        current_visit = self.object
        
        # Dobij novi broj dana
        novi_broj_dana = form.cleaned_data.get('broj_dana_posete')
        
        # Ako nema group_id ili nema broja dana, standardno ažuriranje
        if not current_visit.group_id or not novi_broj_dana or novi_broj_dana < 1:
            return super().form_valid(form)
        
        # Zaokruži na ceo broj
        novi_broj_dana_int = int(novi_broj_dana)
        
        # Pronađi sve posete u istoj grupi, sortirane po datumu
        group_visits = SrbijaTim.objects.filter(
            group_id=current_visit.group_id
        ).order_by('visit_date')
        
        trenutni_broj_zapisa = group_visits.count()
        
        # Ako se broj dana nije promenio, samo ažuriraj sve zapise u grupi
        if novi_broj_dana_int == trenutni_broj_zapisa:
            # Ažuriraj sve zapise u grupi sa novim podacima
            for visit in group_visits:
                visit.certificate_number = form.cleaned_data.get('certificate_number')
                visit.company = form.cleaned_data.get('company')
                visit.certificate_expiry_date = form.cleaned_data.get('certificate_expiry_date')
                visit.visit_time = form.cleaned_data.get('visit_time')
                visit.broj_dana_posete = novi_broj_dana
                visit.status = form.cleaned_data.get('status')
                visit.report_sent = form.cleaned_data.get('report_sent')
                visit.notes = form.cleaned_data.get('notes')
                visit.save()
                
                # Ažuriraj many-to-many relacije
                standards = form.cleaned_data.get('standards')
                auditors = form.cleaned_data.get('auditors')
                if standards:
                    visit.standards.set(standards)
                if auditors:
                    visit.auditors.set(auditors)
            
            messages.success(self.request, f'Uspešno ažurirano {trenutni_broj_zapisa} poseta.')
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.success_url)
        
        # Ako treba dodati zapise
        elif novi_broj_dana_int > trenutni_broj_zapisa:
            broj_za_dodati = novi_broj_dana_int - trenutni_broj_zapisa
            
            # Ažuriraj postojeće zapise
            for visit in group_visits:
                visit.certificate_number = form.cleaned_data.get('certificate_number')
                visit.company = form.cleaned_data.get('company')
                visit.certificate_expiry_date = form.cleaned_data.get('certificate_expiry_date')
                visit.visit_time = form.cleaned_data.get('visit_time')
                visit.broj_dana_posete = novi_broj_dana
                visit.status = form.cleaned_data.get('status')
                visit.report_sent = form.cleaned_data.get('report_sent')
                visit.notes = form.cleaned_data.get('notes')
                visit.save()
                
                standards = form.cleaned_data.get('standards')
                auditors = form.cleaned_data.get('auditors')
                if standards:
                    visit.standards.set(standards)
                if auditors:
                    visit.auditors.set(auditors)
            
            # Dobij poslednji datum iz grupe
            last_visit = group_visits.last()
            last_date = last_visit.visit_date
            
            # Dodaj nove zapise
            for i in range(1, broj_za_dodati + 1):
                new_date = last_date + timedelta(days=i)
                
                new_visit = SrbijaTim(
                    certificate_number=form.cleaned_data.get('certificate_number'),
                    company=form.cleaned_data.get('company'),
                    certificate_expiry_date=form.cleaned_data.get('certificate_expiry_date'),
                    visit_date=new_date,
                    visit_time=form.cleaned_data.get('visit_time'),
                    broj_dana_posete=novi_broj_dana,
                    group_id=current_visit.group_id,
                    status=form.cleaned_data.get('status'),
                    report_sent=form.cleaned_data.get('report_sent'),
                    notes=form.cleaned_data.get('notes'),
                    created_by=self.request.user
                )
                new_visit.save()
                
                standards = form.cleaned_data.get('standards')
                auditors = form.cleaned_data.get('auditors')
                if standards:
                    new_visit.standards.set(standards)
                if auditors:
                    new_visit.auditors.set(auditors)
            
            messages.success(
                self.request, 
                f'Uspešno ažurirano {trenutni_broj_zapisa} poseta i dodato {broj_za_dodati} novih.'
            )
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.success_url)
        
        # Ako treba ukloniti zapise
        else:  # novi_broj_dana_int < trenutni_broj_zapisa
            broj_za_ukloniti = trenutni_broj_zapisa - novi_broj_dana_int
            
            # Ažuriraj preostale zapise
            visits_to_keep = list(group_visits[:novi_broj_dana_int])
            for visit in visits_to_keep:
                visit.certificate_number = form.cleaned_data.get('certificate_number')
                visit.company = form.cleaned_data.get('company')
                visit.certificate_expiry_date = form.cleaned_data.get('certificate_expiry_date')
                visit.visit_time = form.cleaned_data.get('visit_time')
                visit.broj_dana_posete = novi_broj_dana
                visit.status = form.cleaned_data.get('status')
                visit.report_sent = form.cleaned_data.get('report_sent')
                visit.notes = form.cleaned_data.get('notes')
                visit.save()
                
                standards = form.cleaned_data.get('standards')
                auditors = form.cleaned_data.get('auditors')
                if standards:
                    visit.standards.set(standards)
                if auditors:
                    visit.auditors.set(auditors)
            
            # Obriši poslednje zapise
            visits_to_delete = group_visits[novi_broj_dana_int:]
            for visit in visits_to_delete:
                visit.delete()
            
            messages.success(
                self.request, 
                f'Uspešno ažurirano {novi_broj_dana_int} poseta i uklonjeno {broj_za_ukloniti}.'
            )
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.success_url)
    
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
    # Get filter parametar za auditora
    auditor_id = request.GET.get('auditor')
    
    visits = SrbijaTim.objects.all().prefetch_related('standards', 'auditors')
    
    # Filtriraj po auditoru ako je selektovan
    if auditor_id:
        visits = visits.filter(auditors__id=auditor_id).distinct()
        logger.info(f"Srbija Tim - filtered by auditor {auditor_id}: {visits.count()} visits")
    
    events = []
    for visit in visits:
        # Boja na osnovu statusa i izveštaja
        status = getattr(visit, 'status', 'nije_zakazan')
        
        # Ako je izveštaj poslat (može biti samo za odrađenu posetu)
        if visit.report_sent:
            color = '#28a745'  # Zelena - poslat izveštaj
        # Ako izveštaj nije poslat, boja zavisi od statusa
        elif status == 'zakazan':
            color = '#007bff'  # Plava - zakazan
        elif status == 'nije_zakazan':
            color = '#6c757d'  # Siva - nije zakazan
        elif status == 'odradjena':
            color = '#ffc107'  # Žuta - odrađena poseta (bez izveštaja)
        else:
            color = '#dc3545'  # Crvena - default
        
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
                'status': getattr(visit, 'status', 'nije_zakazan'),
                'report_sent': visit.report_sent,
                'certificate_expiry_date': visit.certificate_expiry_date.isoformat() if visit.certificate_expiry_date else None,
                'notes': visit.notes or '',
                'visit_time': visit_time.isoformat() if visit_time else None,
                'broj_dana_posete': float(visit.broj_dana_posete) if visit.broj_dana_posete else None,
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
def get_company_data(request, company_id):
    """
    API endpoint koji vraća podatke o kompaniji (broj sertifikata i datum isticanja)
    """
    try:
        from .company_models import Company
        company = get_object_or_404(Company, pk=company_id)
        
        # Pronađi najnoviji aktivni ciklus sertifikacije
        latest_cycle = company.certification_cycles.filter(
            status='active'
        ).order_by('-planirani_datum').first()
        
        # Podaci za vraćanje
        data = {
            'success': True,
            'certificate_number': company.certificate_number or '',
            'certificate_expiry_date': None
        }
        
        # Ako postoji aktivan ciklus, izračunaj datum isticanja (3 godine od planiranog datuma)
        if latest_cycle and latest_cycle.planirani_datum:
            from dateutil.relativedelta import relativedelta
            expiry_date = latest_cycle.planirani_datum + relativedelta(years=3)
            data['certificate_expiry_date'] = expiry_date.isoformat()
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f'Greška pri dobijanju podataka o kompaniji: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Greška: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def srbija_tim_update_date(request, pk):
    """
    Ažurira datum i vreme posete preko AJAX-a (za drag & drop)
    Validira da auditor ne može biti na više sastanaka istog dana
    """
    try:
        visit = SrbijaTim.objects.get(pk=pk)
        data = json.loads(request.body)
        
        new_date_str = data.get('visit_date')
        new_time_str = data.get('visit_time')
        
        if not new_date_str:
            return JsonResponse({
                'success': False,
                'message': 'Datum je obavezan.'
            }, status=400)
        
        # Sačuvaj stare vrednosti za logging
        old_date = visit.visit_date
        old_time = getattr(visit, 'visit_time', None)
        
        # Parsiranje datuma
        from datetime import datetime
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        
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
        
        # VALIDACIJA: Proveri da li neki od auditora već ima sastanak tog dana
        auditors = visit.auditors.all()
        conflicts = []
        
        for auditor in auditors:
            # Pronađi sve posete ovog auditora na novi datum (osim trenutne)
            conflicting_visits = SrbijaTim.objects.filter(
                auditors=auditor,
                visit_date=new_date
            ).exclude(pk=visit.pk)
            
            if conflicting_visits.exists():
                # Napravi listu kompanija sa kojima je konflikt
                company_names = [v.company.name for v in conflicting_visits]
                conflicts.append({
                    'auditor': auditor.ime_prezime,
                    'companies': company_names
                })
        
        # Ako ima konflikata, vrati grešku
        if conflicts:
            conflict_messages = []
            for conflict in conflicts:
                companies = ', '.join(conflict['companies'])
                conflict_messages.append(
                    f"{conflict['auditor']} već ima zakazan sastanak tog dana sa: {companies}"
                )
            
            return JsonResponse({
                'success': False,
                'message': 'Konflikt u rasporedu auditora!',
                'conflicts': conflict_messages
            }, status=400)
        
        # Ako nema konflikata, ažuriraj
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
