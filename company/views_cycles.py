from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
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
        sort_by = self.request.GET.get('sort_by', '-start_date')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['sort_by'] = self.request.GET.get('sort_by', '-start_date')
        
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
        context['audits'] = cycle.audits.all().order_by('planned_date')
        
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
                return redirect('company:cycle_detail', pk=cycle.id)
            else:
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
    """Brisanje ciklusa sertifikacije"""
    model = CertificationCycle
    template_name = 'certification_cycles/cycle_confirm_delete.html'
    context_object_name = 'cycle'
    
    def get_success_url(self):
        company = self.object.company
        messages.success(self.request, 'Ciklus sertifikacije je uspešno obrisan.')
        if company:
            return reverse('company:detail', kwargs={'pk': company.pk})
        return reverse('company:cycle_list')


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
    
    def get_success_url(self):
        return reverse('company:cycle_detail', kwargs={'pk': self.object.certification_cycle.pk})


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
        response = super().form_valid(form)
        messages.success(self.request, 'Audit je uspešno ažuriran.')
        return response
    
    def get_success_url(self):
        return reverse('company:cycle_detail', kwargs={'pk': self.object.certification_cycle.pk})


class CycleAuditDeleteView(LoginRequiredMixin, DeleteView):
    """Brisanje audita"""
    model = CycleAudit
    template_name = 'certification_cycles/audit_confirm_delete.html'
    context_object_name = 'audit'
    
    def get_success_url(self):
        cycle = self.object.certification_cycle
        messages.success(self.request, 'Audit je uspešno obrisan.')
        return reverse('company:cycle_detail', kwargs={'pk': cycle.pk})
