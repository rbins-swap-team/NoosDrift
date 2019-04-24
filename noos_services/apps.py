from django.apps import AppConfig


class NoosServicesConfig(AppConfig):
    name = 'noos_services'

    def ready(self):
        # Don't remove imports
        import noos_services.signals
