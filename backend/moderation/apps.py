from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moderation"

    def ready(self):
        import os

        # Avoid running twice in Django dev server's autoreload process
        if os.environ.get("RUN_MAIN") != "true":
            from moderation.inference import preload

            preload()
