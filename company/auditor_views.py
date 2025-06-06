from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
import logging

from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from .standard_models import StandardDefinition, CompanyStandard
from .iaf_models import IAFEACCode
from .auditor_forms import AuditorForm, AuditorStandardForm, AuditorStandardIAFEACForm
from .cycle_models import CycleAudit
from .company_models import Company
from .audit_utils import is_auditor_qualified_for_company, is_auditor_qualified_for_audit, get_qualified_auditors_for_company, get_qualified_auditors_for_audit

# Konfigurisanje logera
logger = logging.getLogger(__name__)

class AuditorListView(LoginRequiredMixin, ListView):
    model = Auditor
    template_name = 'company/auditor_list.html'
    context_object_name = 'auditors'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Auditor.objects.all().prefetch_related(
            'auditor_standardi__standard',
            'auditor_standardi__iaf_eac_links__iaf_eac_code'
        )
        
        # Filtriranje po kategoriji ako je zahtevano
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(kategorija=category)
        
        # Filtriranje po standardu ako je zahtevano
        standard_id = self.request.GET.get('standard')
        if standard_id:
            queryset = queryset.filter(auditor_standardi__standard_id=standard_id).distinct()
        
        # Filtriranje po IAF/EAC kodu ako je zahtevano
        iaf_code = self.request.GET.get('iaf_code')
        if iaf_code:
            queryset = queryset.filter(
                auditor_standardi__iaf_eac_links__iaf_eac_code__iaf_code=iaf_code
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Lista auditora'
        context['category_choices'] = Auditor.AUDITOR_CATEGORY_CHOICES
        context['standards'] = StandardDefinition.objects.all()
        context['iaf_codes'] = IAFEACCode.objects.all()
        
        # Trenutno izabrani filteri
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_standard'] = self.request.GET.get('standard', '')
        context['selected_iaf_code'] = self.request.GET.get('iaf_code', '')
        
        return context


class AuditorDetailView(LoginRequiredMixin, DetailView):
    model = Auditor
    template_name = 'company/auditor_detail.html'
    context_object_name = 'auditor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Detalji auditora: {self.object.ime_prezime}'
        
        # Dohvati sve standarde auditora sa IAF/EAC kodovima
        auditor_standards = AuditorStandard.objects.filter(auditor=self.object).prefetch_related(
            'standard',
            'iaf_eac_links__iaf_eac_code'
        )
        context['auditor_standards'] = auditor_standards
        
        return context


class AuditorCreateView(LoginRequiredMixin, CreateView):
    model = Auditor
    form_class = AuditorForm
    template_name = 'company/auditor_form.html'
    success_url = reverse_lazy('company:auditor_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novi auditor'
        context['submit_text'] = 'Sačuvaj'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Auditor {form.instance.ime_prezime} je uspešno kreiran.")
        return response


class AuditorUpdateView(LoginRequiredMixin, UpdateView):
    model = Auditor
    form_class = AuditorForm
    template_name = 'company/auditor_form.html'
    success_url = reverse_lazy('company:auditor_list')
    context_object_name = 'auditor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Izmena auditora: {self.object.ime_prezime}'
        context['submit_text'] = 'Sačuvaj izmene'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Auditor {form.instance.ime_prezime} je uspešno izmenjen.")
        return response


class AuditorDeleteView(LoginRequiredMixin, DeleteView):
    model = Auditor
    success_url = reverse_lazy('company:auditor_list')
    template_name = 'company/auditor_confirm_delete.html'
    context_object_name = 'auditor'
    
    def get(self, request, *args, **kwargs):
        # Prikazujemo stranicu za potvrdu brisanja
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        auditor = self.get_object()
        auditor_name = auditor.ime_prezime
        
        try:
            auditor.delete()
            messages.success(request, f'Auditor {auditor_name} je uspešno obrisan.')
            return redirect('company:auditor_list')
        except Exception as e:
            messages.error(request, f'Greška prilikom brisanja auditora: {str(e)}')
            return redirect('company:auditor_list')
    
    # Pregazimo metodu delete da bi koristila našu post metodu
    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
def auditor_standard_create(request, auditor_id):
    """View za dodavanje novog standarda auditoru"""
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    
    if request.method == 'POST':
        form = AuditorStandardForm(request.POST)
        if form.is_valid():
            standard = form.save(commit=False)
            standard.auditor = auditor
            
            # Provera da li već postoji veza sa ovim standardom
            existing = AuditorStandard.objects.filter(
                auditor=auditor, 
                standard=form.cleaned_data['standard']
            ).first()
            
            if existing:
                messages.error(request, f'Auditor već ima dodeljen standard {form.cleaned_data["standard"].code}.')
                return redirect('company:auditor_detail', pk=auditor.id)
            
            standard.save()
            messages.success(request, f'Standard {standard.standard.code} je uspešno dodeljen auditoru {auditor.ime_prezime}.')
            return redirect('company:auditor_detail', pk=auditor.id)
    else:
        form = AuditorStandardForm()
    
    context = {
        'title': f'Dodavanje standarda za auditora: {auditor.ime_prezime}',
        'form': form,
        'auditor': auditor,
        'submit_text': 'Sačuvaj'
    }
    
    return render(request, 'company/auditor_standard_form.html', context)


@login_required
def auditor_standard_update(request, auditor_id, pk):
    """View za izmenu postojećeg standarda auditora - potpuno zaobilazak forme"""
    from django.db import connection
    from django.utils import timezone
    import json
    
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    standard = get_object_or_404(AuditorStandard, pk=pk, auditor=auditor)
    
    if request.method == 'POST':
        # Dodaj debug informaciju
        print(f"DEBUG: POST data = {request.POST}")
        messages.info(request, f"POST podaci: {json.dumps(dict(request.POST))}")
        
        try:
            # Uvek koristimo isti standard ID, ne menjamo standard! To je ključ rešenja!
            standard_id = standard.standard.id
            
            # Samo želimo da ažuriramo datum ili napomenu
            datum_str = request.POST.get('datum_potpisivanja', '')
            datum = None
            if datum_str:
                from datetime import datetime
                datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
                
            napomena = request.POST.get('napomena', '')
            
            # Direktno ažuriranje baze zaobilazeći Django ORM validaciju
            with connection.cursor() as cursor:
                # Primeti da ovde ne menjamo standard_id - ostaje isti!
                query = """
                UPDATE company_auditorstandard 
                SET datum_potpisivanja = %s,
                    napomena = %s,
                    updated_at = %s
                WHERE id = %s
                """
                
                params = [datum, napomena, timezone.now(), pk]
                cursor.execute(query, params)
                
            messages.success(request, f'Standard {standard.standard.code} je uspešno ažuriran za auditora {auditor.ime_prezime}.')
            return redirect('company:auditor_detail', pk=auditor.id)
        except Exception as e:
            messages.error(request, f'Greška prilikom ažuriranja: {str(e)}')
            return redirect('company:auditor_detail', pk=auditor.id)
    
    # Za GET prikaži detalje standarda koje želimo ažurirati
    # Dobavi sve aktivne standarde za dropdown
    all_standards = StandardDefinition.objects.filter(active=True).order_by('code')
    
    context = {
        'title': f'Izmena standarda {standard.standard.code} za auditora: {auditor.ime_prezime}',
        'all_standards': all_standards,
        'current_standard': standard.standard,
        'datum': standard.datum_potpisivanja,
        'napomena': standard.napomena or '',
        'auditor': auditor,
        'standard_id': pk,
        'auditor_id': auditor_id,
        'submit_text': 'Sačuvaj izmene'
    }
    
    # Koristimo prilagođeni template koji ne koristi Django formu
    return render(request, 'company/auditor_standard_manual_edit.html', context)



@login_required
def auditor_standard_delete(request, auditor_id, pk):
    """View za brisanje standarda auditora"""
    auditor = get_object_or_404(Auditor, pk=auditor_id)
    standard = get_object_or_404(AuditorStandard, pk=pk, auditor=auditor)
    standard_code = standard.standard.code
    
    if request.method == 'POST':
        try:
            standard.delete()
            messages.success(request, f'Standard {standard_code} je uspešno obrisan za auditora {auditor.ime_prezime}.')
        except Exception as e:
            messages.error(request, f'Greška prilikom brisanja standarda: {str(e)}')
        
        return redirect('company:auditor_detail', pk=auditor.id)
    
    context = {
        'title': f'Brisanje standarda {standard_code} za auditora: {auditor.ime_prezime}',
        'auditor': auditor,
        'standard': standard,
        'cancel_url': reverse_lazy('company:auditor_detail', kwargs={'pk': auditor.id})
    }
    
    return render(request, 'company/auditor_standard_confirm_delete.html', context)


@login_required
def auditor_standard_iaf_eac_create(request, standard_id):
    """View za dodavanje IAF/EAC koda standardu auditora"""
    auditor_standard = get_object_or_404(AuditorStandard, pk=standard_id)
    auditor = auditor_standard.auditor
    
    if request.method == 'POST':
        form = AuditorStandardIAFEACForm(request.POST)
        if form.is_valid():
            iaf_eac = form.save(commit=False)
            iaf_eac.auditor_standard = auditor_standard
            
            # Provera da li već postoji veza sa ovim IAF/EAC kodom
            existing = AuditorStandardIAFEACCode.objects.filter(
                auditor_standard=auditor_standard, 
                iaf_eac_code=form.cleaned_data['iaf_eac_code']
            ).first()
            
            if existing:
                messages.error(request, f'Standard već ima dodeljen IAF/EAC kod {form.cleaned_data["iaf_eac_code"]}.')
                return redirect('company:auditor_detail', pk=auditor.id)
            
            iaf_eac.save()
            messages.success(request, f'IAF/EAC kod {iaf_eac.iaf_eac_code} je uspešno dodeljen standardu {auditor_standard.standard.code}.')
            return redirect('company:auditor_detail', pk=auditor.id)
    else:
        form = AuditorStandardIAFEACForm()
    
    context = {
        'title': f'Dodavanje IAF/EAC koda za standard {auditor_standard.standard.code}',
        'form': form,
        'auditor': auditor,
        'auditor_standard': auditor_standard,
        'submit_text': 'Sačuvaj'
    }
    
    return render(request, 'company/auditor_standard_iaf_eac_form.html', context)


@login_required
def auditor_standard_iaf_eac_update(request, standard_id, pk):
    """View za izmenu IAF/EAC koda standardu auditora sa direktnim SQL pristupom"""
    auditor_standard = get_object_or_404(AuditorStandard, pk=standard_id)
    auditor = auditor_standard.auditor
    iaf_eac = get_object_or_404(AuditorStandardIAFEACCode, pk=pk, auditor_standard=auditor_standard)
    
    # Sačuvaj trenutni IAF/EAC kod pre bilo kakvih izmena
    current_iaf_eac_code = iaf_eac.iaf_eac_code
    
    if request.method == 'POST':
        # Ne koristimo formu za validaciju - direktno čitamo iz POST podataka
        # Jedina polja koja dozvoljavamo da se menjaju su is_primary i notes
        from django.db import connection
        
        is_primary = 'is_primary' in request.POST
        notes = request.POST.get('notes', '')
        
        # Debug poruke
        print(f"DEBUG: Updating IAF/EAC code {pk} - is_primary={is_primary}, notes={notes}")
        
        # Ako je označen kao primarni, poništi sve druge primarne kodove za ovaj standard
        if is_primary:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE company_auditorstandardiafeaccode SET is_primary = %s WHERE auditor_standard_id = %s AND id != %s",
                    [False, auditor_standard.id, pk]
                )
        
        # Ažuriraj samo is_primary i notes za IAF/EAC kod
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE company_auditorstandardiafeaccode SET is_primary = %s, notes = %s WHERE id = %s",
                [is_primary, notes, pk]
            )
        
        messages.success(request, f'IAF/EAC kod {current_iaf_eac_code} je uspešno ažuriran za standard {auditor_standard.standard.code}.')
        return redirect('company:auditor_detail', pk=auditor.id)
    else:
        # Za GET zahtev, prikažemo formu ali isključimo mogućnost promene samog IAF/EAC koda
        form = AuditorStandardIAFEACForm(instance=iaf_eac)
    
    context = {
        'title': f'Izmena IAF/EAC koda za standard {auditor_standard.standard.code}',
        'form': form,
        'auditor': auditor,
        'auditor_standard': auditor_standard,
        'iaf_eac': iaf_eac,
        'current_iaf_eac_code': current_iaf_eac_code,
        'submit_text': 'Sačuvaj'
    }
    
    # Koristi specijalni template za manualnu izmenu, koji ne dozvoljava promenu IAF/EAC koda
    return render(request, 'company/auditor_standard_iaf_eac_manual_edit.html', context)


@login_required
def auditor_standard_iaf_eac_delete(request, standard_id, pk):
    """View za brisanje IAF/EAC koda standarda auditora"""
    auditor_standard = get_object_or_404(AuditorStandard, pk=standard_id)
    auditor = auditor_standard.auditor
    iaf_eac = get_object_or_404(AuditorStandardIAFEACCode, pk=pk, auditor_standard=auditor_standard)
    
    if request.method == 'POST':
        iaf_eac_code = str(iaf_eac.iaf_eac_code)
        iaf_eac.delete()
        messages.success(request, f'IAF/EAC kod {iaf_eac_code} je uspešno obrisan.')
        return redirect('company:auditor_detail', pk=auditor.id)
    
    context = {
        'title': 'Brisanje IAF/EAC koda',
        'object': iaf_eac,
        'auditor': auditor,
        'auditor_standard': auditor_standard,
        'cancel_url': reverse('company:auditor_detail', kwargs={'pk': auditor.id})
    }
    
    return render(request, 'company/generic_confirm_delete.html', context)


def check_auditor_qualification_for_company(auditor_id, company_id):
    """Proverava da li je auditor kvalifikovan za standarde koje kompanija ima"""
    is_qualified, missing_standards_list = is_auditor_qualified_for_company(auditor_id, company_id)
    
    # Formatiramo nedostajuće standarde u format pogodan za JSON
    missing_standards = []
    for std in missing_standards_list:
        missing_standards.append({
            'id': std.id,
            'code': std.code,
            'name': std.standard
        })
    
    # Pripremamo poruku
    if is_qualified:
        message = 'Auditor je kvalifikovan za sve standarde kompanije'
    else:
        standard_codes = ', '.join([s['code'] for s in missing_standards])
        message = f'Auditor nije kvalifikovan za sledeće standarde: {standard_codes}'
    
    return {
        'is_qualified': is_qualified,
        'missing_standards': missing_standards,
        'message': message
    }


def check_auditor_qualification_for_audit(auditor_id, audit_id):
    """Proverava da li je auditor kvalifikovan za audit na osnovu standarda u ciklusu sertifikacije"""
    try:
        is_qualified, missing_standards_list = is_auditor_qualified_for_audit(auditor_id, audit_id)
        
        # Formatiramo nedostajuće standarde u format pogodan za JSON
        missing_standards = []
        for std in missing_standards_list:
            missing_standards.append({
                'id': std.id,
                'code': std.code,
                'name': std.standard
            })
        
        # Pripremamo poruku
        if is_qualified:
            message = 'Auditor je kvalifikovan za sve standarde u ciklusu'
        else:
            standard_codes = ', '.join([s['code'] for s in missing_standards])
            message = f'Auditor nije kvalifikovan za sledeće standarde: {standard_codes}'
        
        return {
            'is_qualified': is_qualified,
            'missing_standards': missing_standards,
            'message': message
        }
    except Exception as e:
        return {'is_qualified': False, 'missing_standards': [], 'message': str(e)}


@login_required
def get_qualified_auditors(request):
    """API endpoint za dohvatanje kvalifikovanih auditora za kompaniju ili audit"""
    company_id = request.GET.get('company_id')
    audit_id = request.GET.get('audit_id')
    
    if not company_id and not audit_id:
        return JsonResponse({'success': False, 'message': 'Morate proslediti company_id ili audit_id'}, status=400)
    
    try:
        # Ako je prosleđen audit_id, dohvatamo kvalifikovane auditore za taj audit
        if audit_id:
            qualified_auditors_list = get_qualified_auditors_for_audit(audit_id)
            
            # Formatiramo rezultat za JSON odgovor
            qualified_auditors = []
            for auditor in qualified_auditors_list:
                qualified_auditors.append({
                    'id': auditor.id,
                    'name': auditor.ime_prezime,
                    'email': auditor.email,
                    'category': auditor.get_kategorija_display()
                })
        
        # Ako je prosleđen company_id, dohvatamo kvalifikovane auditore za tu kompaniju
        elif company_id:
            # get_qualified_auditors_for_company vraća rečnik gde su ključevi ID-jevi standarda
            # a vrednosti su liste auditora, pa moramo da transformišemo rezultat
            qualified_auditors_dict = get_qualified_auditors_for_company(company_id)
            
            # Ako nema standarda, svi auditori su kvalifikovani
            if not qualified_auditors_dict:
                auditors = Auditor.objects.all()
                qualified_auditors = [{
                    'id': a.id, 
                    'name': a.ime_prezime,
                    'email': a.email,
                    'category': a.get_kategorija_display()
                } for a in auditors]
                return JsonResponse({'success': True, 'data': qualified_auditors})
            
            # Pronalazimo auditore koji su kvalifikovani za SVE standarde
            all_auditors = set()
            for standard_id, auditors in qualified_auditors_dict.items():
                # Za prvi standard, dodajemo sve auditore
                if len(all_auditors) == 0:
                    all_auditors = set(auditors)
                # Za ostale standarde, zadržavamo samo one koji su u preseku
                else:
                    all_auditors = all_auditors.intersection(set(auditors))
            
            # Formatiramo rezultat za JSON odgovor
            qualified_auditors = [{
                'id': a.id, 
                'name': a.ime_prezime,
                'email': a.email,
                'category': a.get_kategorija_display()
            } for a in all_auditors]
        
        return JsonResponse({'success': True, 'data': qualified_auditors})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_GET
def get_auditor_details(request, pk):
    """API endpoint za dohvatanje detalja o auditoru u JSON formatu"""
    try:
        auditor = get_object_or_404(Auditor, pk=pk)
        
        # Dohvatanje standarda i IAF/EAC kodova
        standards_data = []
        for standard in auditor.auditor_standardi.all().select_related('standard'):
            iaf_eac_codes = []
            for link in standard.iaf_eac_links.all().select_related('iaf_eac_code'):
                iaf_eac_codes.append({
                    'id': link.iaf_eac_code.id,
                    'code': link.iaf_eac_code.iaf_code,
                    'title': link.iaf_eac_code.title,
                    'is_primary': link.is_primary,
                    'notes': link.notes
                })
            
            standards_data.append({
                'id': standard.id,
                'standard_id': standard.standard.id,
                'code': standard.standard.code,
                'name': standard.standard.standard,
                'date_signed': standard.datum_potpisivanja.strftime('%d.%m.%Y') if standard.datum_potpisivanja else None,
                'notes': standard.napomena,
                'iaf_eac_codes': iaf_eac_codes
            })
        
        # Formatiranje kategorije
        category_display = dict(Auditor.AUDITOR_CATEGORY_CHOICES).get(auditor.kategorija, auditor.kategorija)
        
        # Provera da li je zahtevan i company_id za proveru kvalifikacija
        company_id = request.GET.get('company_id')
        company_qualification = None
        if company_id:
            company_qualification = check_auditor_qualification_for_company(auditor.id, company_id)
        
        # Provera da li je zahtevan i audit_id za proveru kvalifikacija
        audit_id = request.GET.get('audit_id')
        audit_qualification = None
        if audit_id:
            audit_qualification = check_auditor_qualification_for_audit(auditor.id, audit_id)
        
        # Priprema podataka za JSON odgovor
        data = {
            'id': auditor.id,
            'name': auditor.ime_prezime,
            'email': auditor.email,
            'phone': auditor.telefon,
            'category': auditor.kategorija,
            'category_display': category_display,
            'standards': standards_data,
            'created_at': auditor.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': auditor.updated_at.strftime('%d.%m.%Y %H:%M')
        }
        
        # Dodajemo informacije o kvalifikacijama ako su zahtevane
        if company_qualification:
            data['company_qualification'] = company_qualification
        
        if audit_qualification:
            data['audit_qualification'] = audit_qualification
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
