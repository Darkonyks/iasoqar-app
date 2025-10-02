from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from .cycle_models import CertificationCycle, CycleStandard, CycleAudit
from .models import Company
from .forms import CertificationCycleForm, CycleAuditForm
from .standard_models import StandardDefinition


class CertificationCycleListView(LoginRequiredMixin, ListView):
    """Prikaz liste ciklusa sertifikacije"""
    model = CertificationCycle
    template_name = 'certification_cycles/cycle_list.html'
    context_object_name = 'cycles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by company if specified
        company_id = self.kwargs.get('company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(company__name__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Sort options
        sort_by = self.request.GET.get('sort_by', '-planirani_datum')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['sort_by'] = self.request.GET.get('sort_by', '-planirani_datum')
        
        # Add company context if filtering by company
        company_id = self.kwargs.get('company_id')
        if company_id:
            context['company'] = get_object_or_404(Company, id=company_id)
        
        # Add status choices for filtering
        context['status_choices'] = CertificationCycle.STATUS_CHOICES
        
        return context


class CertificationCycleDetailView(LoginRequiredMixin, DetailView):
    """Prikaz detalja ciklusa sertifikacije"""
    model = CertificationCycle
    template_name = 'certification_cycles/cycle_detail.html'
    context_object_name = 'cycle'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cycle = self.object
        
        # Get standards for this cycle
        context['standards'] = cycle.cycle_standards.all()
        
        # Get audits for this cycle
        context['audits'] = (
            cycle.audits
            .select_related('lead_auditor')
            .prefetch_related('audit_team')
            .order_by('planned_date')
        )
        
        # Check if we need to show audit form
        edit_audit = self.request.GET.get('edit_audit')
        if edit_audit:
            audit = get_object_or_404(CycleAudit, id=edit_audit, certification_cycle=cycle)
            context['audit_form'] = CycleAuditForm(instance=audit)
            context['show_audit_form'] = True
            context['editing_audit'] = audit
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        cycle = self.object
        
        # Handle audit form submission
        if 'submit_audit_form' in request.POST:
            audit_id = request.POST.get('audit_id')
            if audit_id:
                # Editing existing audit
                audit = get_object_or_404(CycleAudit, id=audit_id, certification_cycle=cycle)
                form = CycleAuditForm(request.POST, instance=audit, request=request)
            else:
                # Creating new audit
                form = CycleAuditForm(request.POST, request=request)
            
            if form.is_valid():
                audit = form.save()
                messages.success(request, 'Audit je uspešno sačuvan.')
                # Nakon čuvanja preusmeri na kalendar (bez potrebe za ručnim osvežavanjem)
                return redirect('company:calendar')
            else:
                # Jasna notifikacija kada postoje konflikti rezervacija auditora
                non_field_errs = [str(e) for e in form.non_field_errors()]
                has_conflict = (
                    'lead_auditor' in form.errors or
                    'audit_team' in form.errors or
                    any('konflikt' in e.lower() for e in non_field_errs)
                )
                if has_conflict:
                    messages.error(request, 'Konflikt rezervacije auditora: jedan ili više auditora su već rezervisani za izabrane datume. Proverite označena polja.')
                else:
                    messages.error(request, 'Greška pri čuvanju audita. Proverite formular.')

                context = self.get_context_data(**kwargs)
                context['audit_form'] = form
                context['show_audit_form'] = True
                if audit_id:
                    context['editing_audit'] = get_object_or_404(CycleAudit, id=audit_id)
                return render(request, self.template_name, context)
        
        return super().get(request, *args, **kwargs)


class CertificationCycleCreateView(LoginRequiredMixin, CreateView):
    """Kreiranje novog ciklusa sertifikacije"""
    model = CertificationCycle
    form_class = CertificationCycleForm
    template_name = 'certification_cycles/cycle_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        company_id = self.kwargs.get('company_id')
        if company_id:
            initial['company'] = company_id
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novi ciklus sertifikacije'
        
        # Add company context if creating for specific company
        company_id = self.kwargs.get('company_id')
        if company_id:
            context['company'] = get_object_or_404(Company, id=company_id)
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ciklus sertifikacije je uspešno kreiran.')
        return response
    
    def get_success_url(self):
        if self.object.company:
            return reverse('company:detail', kwargs={'pk': self.object.company.pk})
        return reverse('company:cycle_list')


class CertificationCycleUpdateView(LoginRequiredMixin, UpdateView):
    """Ažuriranje postojećeg ciklusa sertifikacije"""
    model = CertificationCycle
    form_class = CertificationCycleForm
    template_name = 'certification_cycles/cycle_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmena ciklusa sertifikacije'
        context['company'] = self.object.company
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ciklus sertifikacije je uspešno ažuriran.')
        return response
    
    def get_success_url(self):
        return reverse('company:cycle_detail', kwargs={'pk': self.object.pk})


class CertificationCycleDeleteView(LoginRequiredMixin, DeleteView):
    """Brisanje ciklusa sertifikacije sa kaskadnim brisanjem povezanih zapisa"""
    model = CertificationCycle
    template_name = 'certification_cycles/cycle_confirm_delete.html'
    context_object_name = 'cycle'
    
    def get_success_url(self):
        """URL za redirekciju nakon uspešnog brisanja (koristi se u super().delete())."""
        company_id = getattr(self.object, 'company_id', None)
        if company_id:
            return reverse('company:detail', kwargs={'pk': company_id})
        return reverse('company:cycle_list')
    
    def post(self, request, *args, **kwargs):
        """Kaskadno brisanje ciklusa sertifikacije i povezanih zapisa"""
        self.object = self.get_object()
        company_id = self.object.company.id  # Čuvamo ID kompanije pre brisanja
        
        try:
            # Prvo brišemo sve audit_days za svaki audit
            for audit in self.object.audits.all():
                audit.audit_days.all().delete()
            
            # Zatim brišemo sve audite
            self.object.audits.all().delete()
            
            # Brišemo sve cycle_standards
            self.object.cycle_standards.all().delete()
            
            # Na kraju brišemo sam ciklus kroz parent klasu
            response = super().delete(request, *args, **kwargs)
            
            messages.success(request, 'Ciklus sertifikacije je uspešno obrisan zajedno sa svim povezanim zapisima.')
            return redirect('company:detail', pk=company_id)
            
        except Exception as e:
            messages.error(request, f'Greška prilikom brisanja ciklusa sertifikacije: {str(e)}')
            return redirect('company:cycle_detail', pk=self.object.pk)


# Views for managing audits
class CycleAuditCreateView(LoginRequiredMixin, CreateView):
    """Kreiranje novog audita u ciklusu"""
    model = CycleAudit
    form_class = CycleAuditForm
    template_name = 'certification_cycles/audit_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        cycle_id = self.kwargs.get('cycle_id')
        if cycle_id:
            initial['certification_cycle'] = cycle_id
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novi audit'
        
        # Add cycle context
        cycle_id = self.kwargs.get('cycle_id')
        if cycle_id:
            cycle = get_object_or_404(CertificationCycle, id=cycle_id)
            context['cycle'] = cycle
            context['company'] = cycle.company
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Audit je uspešno kreiran.')
        return response

    def form_invalid(self, form):
        # Jasna poruka o konfliktu rezervacija (ako postoji)
        non_field_errs = [str(e) for e in form.non_field_errors()]
        has_conflict = (
            'lead_auditor' in form.errors or
            'audit_team' in form.errors or
            any('konflikt' in e.lower() for e in non_field_errs)
        )
        if has_conflict:
            messages.error(self.request, 'Konflikt rezervacije auditora: jedan ili više auditora su već rezervisani za izabrane datume. Proverite označena polja.')
        else:
            messages.error(self.request, 'Greška pri čuvanju audita. Proverite formular.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Nakon kreiranja audita, preusmeri na kalendar
        return reverse('company:calendar')


class CycleAuditUpdateView(LoginRequiredMixin, UpdateView):
    """Ažuriranje postojećeg audita"""
    model = CycleAudit
    form_class = CycleAuditForm
    template_name = 'certification_cycles/audit_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmena audita'
        context['cycle'] = self.object.certification_cycle
        context['company'] = self.object.certification_cycle.company
        return context
    
    def form_valid(self, form):
        # Sačuvaj prethodni status i stvarni datum pre čuvanja forme
        previous_status = self.object.audit_status
        previous_actual_date = self.object.actual_date
        
        # Sačuvaj formu
        response = super().form_valid(form)
        
        # Ako je status promenjen na 'completed' i postavljen je stvarni datum
        if (form.cleaned_data['audit_status'] == 'completed' and 
            form.cleaned_data['actual_date'] and 
            (previous_status != 'completed' or not previous_actual_date)):
            
            try:
                # Obriši sve planirane dane audita
                deleted_count = self.object.audit_days.filter(is_planned=True, is_actual=False).delete()[0]
                if deleted_count > 0:
                    messages.info(self.request, f'Obrisano je {deleted_count} planiranih dana audita.')
            except Exception as e:
                messages.warning(self.request, f'Greška prilikom brisanja planiranih dana audita: {str(e)}')
        
        messages.success(self.request, 'Audit je uspešno ažuriran.')
        return response
    
    def form_invalid(self, form):
        # Jasna poruka o konfliktu rezervacija (ako postoji)
        non_field_errs = [str(e) for e in form.non_field_errors()]
        has_conflict = (
            'lead_auditor' in form.errors or
            'audit_team' in form.errors or
            any('konflikt' in e.lower() for e in non_field_errs)
        )
        if has_conflict:
            messages.error(self.request, 'Konflikt rezervacije auditora: jedan ili više auditora su već rezervisani za izabrane datume. Proverite označena polja.')
        else:
            messages.error(self.request, 'Greška pri čuvanju audita. Proverite formular.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Proveravamo da li su prosleđeni parametri za kalendar prikaz
        calendar_month = self.request.GET.get('calendar_month')
        calendar_year = self.request.GET.get('calendar_year')
        
        if calendar_month and calendar_year:
            # Vraćamo korisnika na isti mesec i godinu u kalendaru
            return f"{reverse('company:calendar')}?month={calendar_month}&year={calendar_year}"
        else:
            # Fallback na standardni kalendar
            return reverse('company:calendar')


class CycleAuditDeleteView(LoginRequiredMixin, DeleteView):
    """Brisanje audita"""
    model = CycleAudit
    template_name = 'certification_cycles/audit_confirm_delete.html'
    context_object_name = 'audit'
    
    def get_success_url(self):
        cycle = self.object.certification_cycle
        messages.success(self.request, 'Audit je uspešno obrisan.')
        return reverse('company:cycle_detail', kwargs={'pk': cycle.pk})
