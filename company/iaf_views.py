from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .iaf_models import IAFEACCode, IAFScopeReference


class IAFEACCodeListView(LoginRequiredMixin, ListView):
    """
    View za prikaz svih IAF/EAC kodova sa njihovim IAF Scope Reference-ima
    """
    model = IAFEACCode
    template_name = 'iaf/iaf_eac_code_list.html'
    context_object_name = 'iaf_codes'
    
    def get_queryset(self):
        """Vrati sve IAF/EAC kodove sa related IAF Scope Reference"""
        return IAFEACCode.objects.select_related('iaf_scope_reference').order_by('iaf_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'IAF/EAC Kodovi'
        context['total_codes'] = self.get_queryset().count()
        context['total_scopes'] = IAFScopeReference.objects.count()
        return context
