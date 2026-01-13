from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tools.forms'
    verbose_name = 'Forms & Surveys'
    
    def ready(self):
        """Import signals when app is ready"""
        pass  # Future: import signals for notifications
