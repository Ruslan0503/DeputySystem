from django.apps import AppConfig


class A1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a1'

    def ready(self):
    	import a1.signals