from django.apps import AppConfig


class DataApiConfig(AppConfig):
    name = 'data_api'
    """
    def ready(self):
        from rssUpdater import scheduler
        scheduler.start()
    """
