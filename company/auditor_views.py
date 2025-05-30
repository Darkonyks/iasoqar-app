from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from .auditor_models import Auditor, AuditorStandard, AuditorStandardIAFEACCode
from .standard_models import StandardDefinition
from .iaf_models import IAFEACCode
from .auditor_forms import AuditorForm, AuditorStandardForm, AuditorStandardIAFEACForm


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
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
