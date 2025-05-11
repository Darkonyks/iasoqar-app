from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'company'
    verbose_name = 'Kompanija'
    
    def ready(self):
        # Eksplicitna registracija modela u admin panelu
        import company.admin_register
