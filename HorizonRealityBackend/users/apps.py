from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures that signal receivers are registered when Django starts.
        """
        import users.signals