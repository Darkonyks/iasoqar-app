"""
URL configuration for isoqar_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView, TemplateView
from company.views import dashboard
from massadmin import urls as massadmin_urls
import nested_admin.views

# Eksplicitno pozivamo autodiscover() da bi pronašao sve admin module
admin.autodiscover()

urlpatterns = [
    path('', dashboard, name='home'),
    path('admin/', admin.site.urls),
    # Preusmeravanje za admin/company URL na admin/company/company/
    path('admin/company', RedirectView.as_view(url='/admin/company/company/'), name='admin-company-redirect'),
    path('mass_admin/', include(massadmin_urls)),  # Promenjen URL za massadmin
    path('nested_admin/', include('nested_admin.urls')),
    path('company/', include('company.urls')),
    # Autentifikacija korisnika
    path('accounts/', include('accounts.urls')),
    # Debug stranica za testiranje JavaScript biblioteka
    path('debug/', TemplateView.as_view(template_name='debugging.html'), name='debug'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
