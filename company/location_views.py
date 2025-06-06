from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from .company_models import OstalaLokacija, Company
from .location_forms import LocationForm

class LocationListView(ListView):
    model = OstalaLokacija
    template_name = 'company/location/location-list.html'
    context_object_name = 'locations'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtriranje po kompaniji ako je prosleđen ID kompanije
        company_id = self.request.GET.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
            
        return queryset.select_related('company')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dodajemo informacije o kompaniji ako je filtriranje po kompaniji
        company_id = self.request.GET.get('company', None)
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                context['company'] = company
                context['title'] = f'Lokacije kompanije {company.name}'
            except Company.DoesNotExist:
                pass
        else:
            context['title'] = 'Sve lokacije'
            
        return context

class LocationDetailView(DetailView):
    model = OstalaLokacija
    template_name = 'company/location/location-detail.html'
    context_object_name = 'location'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context

class LocationCreateView(CreateView):
    model = OstalaLokacija
    form_class = LocationForm
    template_name = 'company/location/location-form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Ako je prosleđen ID kompanije, postavljamo je kao inicijalnu vrednost
        company_id = self.request.GET.get('company', None)
        if company_id:
            initial['company'] = company_id
            
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova lokacija'
        context['submit_text'] = 'Sačuvaj'
        
        # Ako je prosleđen ID kompanije, dodajemo informacije o kompaniji
        company_id = self.request.GET.get('company', None)
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                context['company'] = company
                context['title'] = f'Nova lokacija za kompaniju {company.name}'
            except Company.DoesNotExist:
                pass
                
        return context
    
    def get_success_url(self):
        # Ako je lokacija kreirana za određenu kompaniju, vraćamo se na detalje te kompanije
        if self.object.company:
            messages.success(self.request, f'Lokacija "{self.object.name}" je uspešno kreirana.')
            return reverse_lazy('company:detail', kwargs={'pk': self.object.company.pk})
        return reverse_lazy('company:location_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Lokacija "{form.instance.name}" je uspešno kreirana.')
        return super().form_valid(form)

class LocationUpdateView(UpdateView):
    model = OstalaLokacija
    form_class = LocationForm
    template_name = 'company/location/location-form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Izmena lokacije {self.object.name}'
        context['submit_text'] = 'Sačuvaj izmene'
        context['company'] = self.object.company
        return context
    
    def get_success_url(self):
        messages.success(self.request, f'Lokacija "{self.object.name}" je uspešno izmenjena.')
        return reverse_lazy('company:detail', kwargs={'pk': self.object.company.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Lokacija "{form.instance.name}" je uspešno izmenjena.')
        return super().form_valid(form)

class LocationDeleteView(DeleteView):
    model = OstalaLokacija
    template_name = 'company/location/location-confirm-delete.html'
    context_object_name = 'location'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Brisanje lokacije {self.object.name}'
        return context
    
    def get_success_url(self):
        company = self.object.company
        messages.success(self.request, f'Lokacija "{self.object.name}" je uspešno obrisana.')
        return reverse_lazy('company:detail', kwargs={'pk': company.pk})
