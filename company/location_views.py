from __future__ import annotations

from typing import TYPE_CHECKING

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .company_models import OstalaLokacija, Company
from .location_forms import LocationForm

if TYPE_CHECKING:
    from django.http import HttpRequest


# ======================================================================
# Mixin – zajednicka logika za rad sa kompanijom iz query-stringa
# ======================================================================

class CompanyFromQueryMixin:
    """Izvlači kompaniju iz GET parametra `company` i dodaje je u kontekst."""

    request: HttpRequest  # type hint za Pylance

    def _get_company_or_none(self) -> Company | None:
        company_id = self.request.GET.get('company')
        if not company_id:
            return None
        return Company.objects.filter(pk=company_id).first()


# ======================================================================
# Views
# ======================================================================

class LocationListView(LoginRequiredMixin, CompanyFromQueryMixin, ListView):
    model = OstalaLokacija
    template_name = 'company/location/location-list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        qs = super().get_queryset().select_related('company')
        company = self._get_company_or_none()
        if company:
            qs = qs.filter(company=company)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self._get_company_or_none()
        if company:
            context['company'] = company
            context['title'] = f'Lokacije kompanije {company.name}'
        else:
            context['title'] = 'Sve lokacije'
        return context


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = OstalaLokacija
    object: OstalaLokacija
    template_name = 'company/location/location-detail.html'
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class LocationCreateView(LoginRequiredMixin, CompanyFromQueryMixin, CreateView):
    model = OstalaLokacija
    object: OstalaLokacija
    form_class = LocationForm
    template_name = 'company/location/location-form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        company = self._get_company_or_none()
        if company:
            kwargs['company_id'] = company.pk
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        company = self._get_company_or_none()
        if company:
            initial['company'] = company.pk
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova lokacija'
        context['submit_text'] = 'Sačuvaj'
        company = self._get_company_or_none()
        if company:
            context['company'] = company
            context['title'] = f'Nova lokacija za kompaniju {company.name}'
        return context

    def get_success_url(self):
        if self.object.company:
            return reverse_lazy('company:detail', kwargs={'pk': self.object.company.pk})
        return reverse_lazy('company:location_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Lokacija "{self.object.name}" je uspešno kreirana.')
        return response


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = OstalaLokacija
    object: OstalaLokacija
    form_class = LocationForm
    template_name = 'company/location/location-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Izmena lokacije {self.object.name}'
        context['submit_text'] = 'Sačuvaj izmene'
        context['company'] = self.object.company
        return context

    def get_success_url(self):
        return reverse_lazy('company:detail', kwargs={'pk': self.object.company.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Lokacija "{self.object.name}" je uspešno izmenjena.')
        return response


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = OstalaLokacija
    object: OstalaLokacija
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
