from django.apps import AppConfig


class NewspaperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newspaper'

    def ready(self):
        import newspaper.signals  # noqa: F401
